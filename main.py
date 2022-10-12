# python pixiv_venv
# -*- encoding: utf-8 -*-
'''
[File]    :   main.py
[Time]    :   2022/10/13 00:21:45
[Author]  :   InaKyui
[Version] :   1.0
[Contact] :   https://github.com/InaKyui
[License] :   (C)Copyright 2022, InaKyui
'''

import os
import pixiv
import sqlite3


if not os.path.exists("pixiv.db"):
    os.mknod("pixiv.db")
# Connect datebase.
pixiv_db = sqlite3.connect("pixiv.db")
cur = pixiv_db.cursor()
# Check table existed.
try:
    cur.execute("SELECT * FROM pixiv_download_record")
except:
    cur.execute("""CREATE TABLE pixiv_download_record
                    (id INT PRIMARY KEY     NOT NULL,
                    download_flag   BOOL    NOT NULL,
                    download_time   TEXT    NOT NULL);""")

# Init class pixiv.
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Referer": "https://www.pixiv.net/"
}
pixiv_mod = pixiv.pixiv(headers, pixiv_db, "image_folder")
pixiv_mod.pixiv_get_list("author","39123643")
#pixiv_mod.pixiv_get_list("daily","20221010")
pixiv_mod.download()
pixiv_db.close()
