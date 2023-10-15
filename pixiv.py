#-*- encoding: utf-8 -*-
#!/usr/bin/pixiv_venv python3.7
"""
[File]        : pixiv.py
[Time]        : 2023/10/10 18:00:00
[Author]      : InaKyui
[License]     : (C)Copyright 2023, InaKyui
[Version]     : 2.1
[Description] : Class pixiv.
"""

__authors__ = ["InaKyui <https://github.com/InaKyui>"]
__version__ = "Version: 2.1"

import os
import re
import json
import time
import random
import datetime
import requests
from database import Database
from selenium import webdriver

# Disable warnings from requests.
requests.packages.urllib3.disable_warnings()

class Pixiv:
    def __init__(self, database:Database) -> None:
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
        time.sleep(60)
        cookie_lst = []
        for item in browser.get_cookies():
            cookie_lst.append("{}={}".format(item["name"], item["value"]))
        cookie = ";".join(cookie_lst)
        self.headers["cookie"] = cookie

    def __get_artworks(self, date:str, task:dict) -> list:
        artworks = []
        for page in range(task["Page"]):
            daily_url = task["URL"].format(date, str(page + 1))
            daily_res = self.session.get(url=daily_url, headers=self.headers, verify=False)
            rank_ptn = re.compile("data-attr=\".*?\" data-id=\".*?\"")
            for rp in rank_ptn.findall(daily_res.text):
                artwork = rp.split("data-id=\"")[1].split("\"")[0]
                artworks.append(artwork)
                print("[Get] Artwork: {}".format(artwork))
        return artworks

    def __get_images(self, artworks:list) -> list:
        images = []
        for artwork in artworks:
            image_info = {}
            time.sleep(random.randint(3,5) / 10)
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
                # TODO Single image -> Multi image.
                image_url = cfs_lst[0].split("\"")[3]
            # Collecting image information.
            image_info["name"] = image_url.split("/")[-1]
            image_info["url"] = image_url
            image_info["artwork"] = artwork
            date_ptn = re.compile("[0-9]{4}\/[0-9]{2}\/[0-9]{2}\/[0-9]{2}\/[0-9]{2}\/[0-9]{2}")
            date_lst = date_ptn.findall(image_url)
            image_info["upload_time"] = date_lst[0].replace("/", "-") if date_lst else ""
            images.append(image_info)
            print("[Get] Image: {}".format(image_info["url"]))
        return images

    def download_image(self, download_path:str, image_info:dict):
        img_rsp = self.session.get(url=image_info["url"], headers=self.headers, verify=False)
        with open(os.path.join(download_path, image_info["url"].split("/")[-1]), "wb") as fw:
            fw.write(img_rsp.content)
        # Supplement and insert image information.
        image_info["download_time"] = datetime.datetime.now()
        self.database.insert_image(image_info)
        time.sleep(random.randint(10, 15) / 10)
        print("[Download] Image: {}".format(image_info["url"]))

    def download(self, start_date, end_date):
        self.__get_cookie()
        print("[Start] Download.")
        # Leaderboard is updated at 12:00 p.m..
        if int(datetime.datetime.now().strftime("%H")) < 12:
            last_date = (datetime.datetime.now() - datetime.timedelta(days=2))
        else:
            last_date = (datetime.datetime.now() - datetime.timedelta(days=1))
        # Whichever is earlier.
        start_date = last_date if last_date < start_date else start_date
        last_date = last_date if last_date < end_date else end_date
        # Closed interval.
        apart_days = last_date.__sub__(start_date).days + 1
        # Download images.
        for i in range(apart_days):
            cur_date = (start_date + datetime.timedelta(days=i)).strftime("%Y%m%d")
            # Determine whether the current date has been downloaded.
            if not self.database.select_date(cur_date):
                for task in self.__task:
                    # Determine whether the download path exists.
                    download_path = os.path.join(os.getcwd(), "images", task["Type"], cur_date)
                    if not os.path.exists(download_path):
                        os.makedirs(download_path)
                    # Date -> [artworks] -> [images].
                    artworks = self.__get_artworks(cur_date, task)
                    images = self.__get_images(artworks)
                    failure_images = []
                    for iu in images:
                        # Determine whether the image has been downloaded.
                        if not self.database.select_image(iu["name"]):
                            try:
                                iu["type"] = task["Type"]
                                self.download_image(download_path, iu)
                            except:
                                failure_images.append(iu)
                    # Second retry for failure images.
                    for fiu in failure_images:
                        try:
                            fiu["type"] = task["Type"]
                            self.download_image(download_path, fiu)
                        except:
                            print("[Fail] {}".format(fiu["url"]))
                self.database.insert_date(cur_date)