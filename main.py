# python pixiv_venv
# -*- encoding: utf-8 -*-
'''
[File]    :   main.py
[Time]    :   2022/10/12 00:47:16
[Author]  :   InaKyui
[Version] :   1.0
[Contact] :   https://github.com/InaKyui
[License] :   (C)Copyright 2022, InaKyui
'''

import pixiv
import sqlite3

pixiv_db = sqlite3.connect("pixiv.db")
# c = pixiv_db.cursor()
# c.execute('''CREATE TABLE save_pixiv_jpg
#        (id INT PRIMARY KEY     NOT NULL,
#        get_in           TEXT    NOT NULL,
#        time            TEXT     NOT NULL);''')

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Referer": "https://www.pixiv.net/"
}
pixiv_mod = pixiv.pixiv(headers, pixiv_db, "image_folder")

pixiv_mod.pixiv_get_list("author","1039353")
pixiv_mod.download()
pixiv_db.close()
