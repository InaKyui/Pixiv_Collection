#-*- encoding: utf-8 -*-
#!/usr/bin/pixiv_venv python3.7
"""
[File]        : main.py
[Time]        : 2023/10/10 18:00:00
[Author]      : InaKyui
[License]     : (C)Copyright 2023, InaKyui
[Version]     : 2.1
[Description] : Class database.
"""

__authors__ = ["InaKyui <https://github.com/InaKyui>"]
__version__ = "Version: 2.1"

import sqlite3
import datetime

class Database:
    def __init__(self, db_name:str):
        self.database = sqlite3.connect(db_name)
        self.cursor = self.database.cursor()

    def create_table(self):
        # Images table.
        sql_create = '''CREATE TABLE images
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         name TEXT NOT NULL,
                         url TEXT NOT NULL,
                         type TEXT NOT NULL,
                         arkwork TEXT NOT NULL,
                         upload_time DATETIME,
                         download_time DATETIME);'''
        self.cursor.execute(sql_create)
        # Dates table.
        sql_create = '''CREATE TABLE dates
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         date TEXT NOT NULL,
                         download_time DATETIME);'''
        self.cursor.execute(sql_create)

    def select_image(self, image_name:str) -> list:
        sql_select = '''SELECT id FROM images WHERE name="{}"'''
        rst = self.cursor.execute(sql_select.format(image_name))
        return rst.fetchall()

    def select_date(self, date:str) -> list:
        sql_select = '''SELECT id FROM dates WHERE date="{}"'''
        rst = self.cursor.execute(sql_select.format(date))
        return rst.fetchall()

    def insert_image(self, image_info:dict):
        sql_insert = '''INSERT INTO images (name, url, type, arkwork, create_time, download_time) VALUES (?,?,?,?,?,?)'''
        data = (image_info["name"],
                image_info["url"],
                image_info["type"],
                image_info["arkwork"],
                image_info["upload_time"],
                image_info["download_time"])
        self.cursor.execute(sql_insert, data)
        self.database.commit()

    def insert_date(self, date:str):
        sql_insert = '''INSERT INTO dates (date, download_time) VALUES (?, ?)'''
        self.cursor.execute(sql_insert, (date, datetime.datetime.now()))
        self.database.commit()