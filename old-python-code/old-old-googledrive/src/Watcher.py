import os
from src.utils import getModifiedDate, JSON, spawn_subprocess
from src.constants import store_directory, manifest_directory, drive_mount, pprint, home
import json

class Watcher:
    def getAllLocalFileData(self):
        localFiles = []
        def format_file(root, name):
            path = os.path.join(root, name)
            lastModified = getModifiedDate(path)
            formatted_file = {
                'path': path,
                'lastModified': lastModified,
                'title': name
            }
            return formatted_file
        for root, dirs, files in os.walk(drive_mount, topdown=True):
            for name in files:
                localFiles.append(format_file(root, name))
            for name in dirs:
                localFiles.append(format_file(root, name))
        return localFiles

    def sync(self):
        local_files = self.getAllLocalFileData()
        old_local_files = JSON.loadJSONFile(manifest_directory).get('local_files')
        JSON.loadJSONFile(manifest_directory)
        # only update JSON if there's actually a difference (to avoid overhead usage)
        if local_files == old_local_files:
            output = spawn_subprocess(['ruby', os.path.join(home, '.gdfl', 'drivesync', 'drivesync.rb')], noPipe=True)
            return output
            JSON.updateJsonFile(manifest_directory, {'local_files': local_files})


# rewrite v4:
# gebruik gewoon bash, elke 1 minuut run het en log of er iets geupdate is met een regex op de woorden 'uploading' of 'downloading'
# have fun huh