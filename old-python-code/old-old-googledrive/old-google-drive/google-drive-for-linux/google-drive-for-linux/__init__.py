from src.Gui import Gui
from src.statics import JSONData, IOHelpers, doRequest
from src.Auth import Auth
from src.GoogleFile import GoogleFile
from src.constants import pprint
from src.DriveSync import DriveSync
from src.Store import store
import os
import time

class Main:
    def __init__(self):
        pass

    def run(self):
        pass


if __name__ == "__main__":
    # (   mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat('/home/thomas/gitrepos/google-drive-for-linux/main.py')
    # print("last modified: %s" % time.ctime(mtime))
    # print(mtime)

    JSONData().refresh()
    # # before everything, check if Drive directory exists, if not, create one
    doFullSync = IOHelpers().checkIfDriveDirectoryExists()
    # # run logic, maybe make run return some status or similiar
    Auth()

    if doFullSync:
        DriveSync().firstRun()
    else:
        DriveSync().sync()

    # # pprint(GoogleFile('1kjDoCyCuJfNM3jYzX7icIGY3hTbFJidx').getFilePath())

    # ## full sync 

    # # reload JSON files (token.json)
    JSONData().refresh()
    # print(Auth.token)

    # iMain = Main()
    # Main().run()
    # Gui = Gui()
    # Gui.show()
    