#-*- encoding: utf-8 -*-
#!/usr/bin/pixiv_venv python3.7
"""
[File]        : main.py
[Time]        : 2023/10/10 18:00:00
[Author]      : InaKyui
[License]     : (C)Copyright 2023, InaKyui
[Version]     : 2.1
[Description] : Code entrance.
"""

__authors__ = ["InaKyui <https://github.com/InaKyui>"]
__version__ = "Version: 2.1"

import os
import argparse
from pixiv import Pixiv
from database import Database
from datetime import datetime

def main(args:argparse.Namespace):
    create_flag = os.path.exists(os.path.join(os.getcwd(), "pixiv.db"))
    pixiv_db = Database("pixiv.db")
    # If the database exists there is no need to create table.
    if not create_flag:
        pixiv_db.create_table()

    # Define the start and end date of the download task.
    start_date = datetime.strptime(args.start_date, "%Y%m%d")
    end_date = datetime.strptime(args.end_date, "%Y%m%d")

    # Download images.
    pixiv = Pixiv(pixiv_db)
    pixiv.download(start_date, end_date)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-debug", "--debug", action="store_true", help="Turn on debug mode.")
    parser.add_argument("-sd", "--start_date", type=str, default=datetime.now().strftime("%Y%m%d"), help="Start date.")
    parser.add_argument("-ed", "--end_date", type=str, default=datetime.now().strftime("%Y%m%d"), help="End date.")
    args = parser.parse_args()
    main(args)