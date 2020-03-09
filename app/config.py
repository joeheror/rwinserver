# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.apps import AppConfig


class MyConfig(AppConfig):
    name = 'cfg'
    patch_path = 'patch/'
    patch_list = {
        "rwin2": {
            "title": "RunningWin2",
            "file_name": "RunningWin2.exe"
        },
        "2fastbet": {
            "title": "2FastBet",
            "file_name": "2FastBet.exe",
        }
    }
