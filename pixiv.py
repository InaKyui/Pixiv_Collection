#-*- encoding: utf-8 -*-
#!/usr/bin/pixiv_venv python3.7
"""
[File]        : pixiv.py
[Time]        : 2023/06/07 18:00:00
[Author]      : InaKyui
[License]     : (C)Copyright 2023, InaKyui
[Version]     : 2.0
[Description] : Class pixiv.
"""

__authors__ = ["InaKyui <https://github.com/InaKyui>"]
__version__ = "Version: 2.0"

import os
import re
import json
import time
import random
import sqlite3
import datetime
import requests
from selenium import webdriver

# Disable warnings from requests.
requests.packages.urllib3.disable_warnings()

class Pixiv:
    def __init__(self, database:sqlite3.Connection) -> None:
        self.__config = None
        self.__load_config()
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Referer": "https://www.pixiv.net/"
        }
        self.database = database
        self.session = requests.Session()

        daily = {
            "Type": "daily",
            "URL": "https://www.pixiv.net/ranking.php?mode=daily&date={0}&p={1}",
            "Page": 10
        }
        daily_ai = {
            "Type": "daily_ai",
            "URL": "https://www.pixiv.net/ranking.php?mode=daily_ai&date={0}&p={1}",
            "Page": 1
        }
        daily_r18 = {
            "Type": "daily_r18",
            "URL": "https://www.pixiv.net/ranking.php?mode=daily_r18&date={0}&p={1}",
            "Page": 2
        }
        daily_ai_r18 = {
            "Type": "daily_r18_ai",
            "URL": "https://www.pixiv.net/ranking.php?mode=daily_r18_ai&date={0}&p={1}",
            "Page": 1
        }
        self.__task = [daily, daily_ai, daily_r18, daily_ai_r18]

    def __load_config(self) -> None:
        with open(os.path.join(os.getcwd(), "config.json"), "r", encoding="utf8") as fr:
            self.__config = json.load(fr)

    def __get_cookie(self):
        chrome_cmd = "{0} --remote-debugging-port=9222 --user-data-dir={1}".format(self.__config["chrome"], os.path.join(os.getcwd(), "selenium\chrome"))
        os.popen(chrome_cmd)

        options = webdriver.ChromeOptions()
        options.debugger_address = "127.0.0.1:9222"
        browser = webdriver.Chrome(options=options)
        time.sleep(3)
        browser.get("https://www.pixiv.net/ranking.php")
        time.sleep(10)
        cookie_lst = []
        for item in browser.get_cookies():
            cookie_lst.append("{}={}".format(item["name"], item["value"]))
        cookie = ";".join(cookie_lst)
        self.headers["cookie"] = cookie

    def __get_artworks(self, task:dict) -> list:
        artworks = []
        if int(datetime.datetime.now().strftime("%H")) < 12:
            last_date = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y%m%d")
        else:
            last_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
        for page in range(task["Page"]):
            daily_url = task["URL"].format(last_date, str(page + 1))
            daily_res = self.session.get(url=daily_url, headers=self.headers, verify=False)
            rank_ptn = re.compile("data-attr=\".*?\" data-id=\".*?\"")
            for artwork in rank_ptn.findall(daily_res.text):
                artworks.append(artwork.split("data-id=\"")[1].split("\"")[0])
        return artworks

    def __get_images(self, artworks:list) -> list:
        images = []
        for artwork in artworks:
            time.sleep(random.randint(1,3) / 10)
            # Get image url.
            artwork_url = "https://www.pixiv.net/artworks/" + artwork
            art_rsp = self.session.get(url=artwork_url, headers=self.headers, verify=False)
            # art_ptn = re.compile("\"urls\":\S+?}")
            img_ptn = re.compile("\"original\"\S*[0-9]{4}/[0-9]{2}/[0-9]{2}/[0-9]{2}/[0-9]{2}/[0-9]{2}/[0-9]{9}_p[0-9]\.\S{3,4}\"")
            cfs_lst = img_ptn.findall(art_rsp.text)
            # \"pageCount\":[0-9]+,
            # Non-moving images.
            if cfs_lst == []:
                print("[Fail] {}".format(artwork_url))
                continue
            else:
                image_url = cfs_lst[0].split("\"")[3]
            images.append(image_url)
        return images

    def download(self):
        self.__get_cookie()

        for task in self.__task:
            download_path = os.path.join(os.getcwd(), "images", task["Type"], datetime.datetime.now().strftime("%Y%m%d"))
            if not os.path.exists(download_path):
                os.mkdir(download_path)

            artworks = self.__get_artworks(task)
            images = self.__get_images(artworks)
            fail_images = []
            for image_url in images:
                try:
                    time.sleep(random.randint(5,10) / 10)
                    img_rsp = self.session.get(url=image_url, headers=self.headers, verify=False)
                    with open(os.path.join(download_path, image_url.split("/")[-1]), "wb") as fw:
                        fw.write(img_rsp.content)
                except:
                    fail_images.append(image_url)

            for fiu in fail_images:
                try:
                    time.sleep(random.randint(5,10) / 10)
                    img_rsp = self.session.get(url=fiu, headers=self.headers, verify=False)
                    with open(os.path.join(download_path, fiu.split("/")[-1]), "wb") as fw:
                        fw.write(img_rsp.content)
                except:
                    print("[Fail] {}".format(image_url))


