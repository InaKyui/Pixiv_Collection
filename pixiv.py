# python pixiv_venv
# -*- encoding: utf-8 -*-
'''
[File]    :   pixiv.py
[Time]    :   2022/10/13 00:20:55
[Author]  :   InaKyui
[Version] :   1.0
[Contact] :   https://github.com/InaKyui
[License] :   (C)Copyright 2022, InaKyui
'''

import os
import time
import aiohttp
import asyncio
import requests
import sqlite3

GET_AUTHOR_ID_LIST_API = "https://www.pixiv.net/ajax/user"
GET_ORIGINAI_JPG_API = "https://i.pximg.net/img-original/img/"
GET_LIST_API = "https://www.pixiv.net/ajax/tags/frequent/illust"

class pixiv:
    def __init__(self, headers:dict, pixiv_db:sqlite3.Connection, download_path:str):
        # headers       : web request header.
        # pixiv_db      : record download information.
        # download_path : local image save path.
        # image_list    : cache image list.
        self.__headers = headers
        self.__pixiv_db = pixiv_db
        self.__download_path = os.path.join(download_path, time.strftime("%H_%M_%S", time.localtime()))
        self.__image_list = []

        # Create download folder.
        if not os.path.exists(self.__download_path):
            os.makedirs(self.__download_path)

    def __link_api(self, url, data=None):
        # Return requests data.
        try:
            res = requests.get(url=url, data=data, headers=self.__headers)
            self.__print_message("Success", "Connection success.")
        except:
            self.__print_message("Error", "Connection failure.")
        return res.json()

    def __save_image_id(self, id:int, download_flag:bool):
        # Save image info.
        spl = "INSERT INTO save_pixiv_jpg (id, download_flag, download_time) VALUES ('{0}','{1}',{2});".format(
            (id, download_flag, time.strftime("%Y%m%d", time.localtime())))
        self.__pixiv_db.execute(spl)
        self.__pixiv_db.commit()

    def __search_image_id(self, id):
        # Find image info from datebase.
        # Return: if data == none: True else: False
        spl = "SELECT * FROM save_pixiv_jpg WHERE id = {0};".format(id)
        data = self.__pixiv_db.execute(spl)
        if not data.fetchall():
            return True
        else:
            return False

    def __print_message(self, status:str, message:str):
        print("[{0}][{1}] {2}".format(time.strftime("%H:%M:%S", time.localtime()), status, message))

    def __pixiv_get_id_list(self, mode, date):
        # Get image list.
        url, image_id_list_tar, image_http_list, http_ = "",[],[],""
        if mode == "author":
            url = os.path.join(GET_AUTHOR_ID_LIST_API, "/{0}/profile/all?lang=zh".format(date))
            http_ = "https://www.pixiv.net/ajax/user/{0}/profile/illusts?".format(date)
        elif mode == "daily":
            url = "https://www.pixiv.net/ranking.php?mode=daily&date={0}".format(date)

        data = self.__link_api(url)
        image_id_list_ori = list(data['body']['illusts'].keys())
        self.__print_message("Debug", "Image List: {0}".format(str(image_id_list_ori)))

        # Uniq image.
        for image_id in image_id_list_ori:
            self.__print_message("Debug", "Image ID: {0}".format(image_id))
            if self.__search_image_id(image_id):
                image_id_list_tar.append(image_id)
        # Get image.
        for target_id in image_id_list_tar:
            http = http_
            http += "ids%5B%5D=" + target_id + "&"
            image_http_list.append(http + "work_category=illustManga&is_first_page=0&lang=zh")

        return image_http_list

    def pixiv_get_list(self, mode, date):
        image_list = []
        image_http_list = self.__pixiv_get_id_list(mode, date)
        for image_http in image_http_list:
            self.__print_message("Debug", "Image Http: {0}".format(image_http))
            data = self.__link_api(image_http)['body']['works']
            for image in data:
                image_address = GET_ORIGINAI_JPG_API + data[image]["url"].split("/", 7)[-1].replace("_custom1200", "").replace("_square1200","")
                image_list.append(image_address)
                self.__print_message("Debug", "Image Address: {0}".format(image_address))

        self.__image_list = image_list
        self.__print_message("Debug", "Image List: {0}".format(str(self.__image_list)))

    def __download_image(self, image_url):
        self.__print_message("Debug", "Url {0}".format(image_url))
        res = requests.get(url=image_url, headers=self.__headers)
        image_name = image_url.split("/")[-1]

        if res.status_code == 404:
            self.__print_message("Done", "%s 404 try png..." % image_name)
            image_name = image_name.replace('.jpg', '.png')
            res = requests.get(url=image_url.replace('.jpg', '.png'), headers=self.__headers)

        with open(os.path.join(self.__download_path, image_name), "wb") as image:
            image.write(res.content)

        # self.__save_image_id(image_name.split("_", 1)[0], image_url)

    async def __async_download_image(self, image_url:str, limit:int):
        url_list = []
        conn = aiohttp.TCPConnector(limit=limit)

        async def download_image(session, url):
            self.__print_message("Debug", "Url {0}".format(url))
            async with session.get(url, headers=self.__headers, verify_ssl=False) as res:
                image_name = str(res.url).split("/")[-1]
                self.__print_message("Debug", "Status {0}".format(res.status))
                if not res.status == 404:
                    content = await res.content.read()
                    with open(os.path.join(self.__download_path, image_name), "wb") as image:
                        image.write(content)
                    self.__save_image_id(image_name.split("_")[0], image_url)
                    self.__print_message("Done", "Remain {0}".format(str(len(self.__image_list))))
                elif res.status == 404:
                    self.__print_message("Done", "%s 404 try png..." % image_name)
                    url_list.append(str(res.url).replace("jpg", "png"))

        async with aiohttp.ClientSession(connector=conn) as session:
            tasks = [asyncio.create_task(download_image(session, image)) for image in [image_url]]
            await asyncio.wait(tasks)

            if not url_list == []:
                await self.__async_download_image(image_url, url_list, limit=limit)

    def download(self,async_http = False,limit=10):
        self.__print_message("Download", "Start...%s"%str(len(self.__image_list)))
        for image_url in self.__image_list:
            if not image_url == "":
                if async_http:
                    try:
                        asyncio.run(self.__async_download_image(image_url, limit=limit))
                    except RuntimeError:
                        pass
                else:
                    self.__download_image(image_url)
        self.__print_message("Done", "Download completed.")
        self.__image_list = []