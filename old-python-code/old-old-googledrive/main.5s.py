#!/usr/bin/env python3
import traceback
from src.utils import check_if_installed, spawn_subprocess, getModifiedDate
from src.constants import home, drive_mount
from src.Store import store
from src.Watcher import Watcher
import threading
import time
from src.Store import store
import os

# This file is called every 5 seconds via Argos
class Main:
    def __init__(self):
        w = Watcher()
        output = w.sync()
        print(output)
        if output:
            print('sad')
        self.render()

    def render(self):
        print(':cloud: :heavy_check_mark:')
        # print('hello')
        # print('---')
        # print('subhello')
        pass


try:
    main = Main()
except Exception as e:
    print('hi')
    print(str("type error: " + str(e)))
    print(traceback.format_exc())