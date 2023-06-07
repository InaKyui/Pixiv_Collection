#-*- encoding: utf-8 -*-
#!/usr/bin/pixiv_venv python3.7
"""
[File]        : main.py
[Time]        : 2023/06/07 18:00:00
[Author]      : InaKyui
[License]     : (C)Copyright 2023, InaKyui
[Version]     : 2.0
[Description] : Code entrance.
"""

__authors__ = ["InaKyui <https://github.com/InaKyui>"]
__version__ = "Version: 2.0"

from pixiv import Pixiv

def main():
    pixiv = Pixiv(None)
    pixiv.download()

if __name__ == "__main__":
    main()