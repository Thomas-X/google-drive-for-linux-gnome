from pathlib import Path
import os
from src.utils import getYAML
import pprint
home = os.path.expanduser(str(Path.home()))
drive_sync_directory = os.path.join(home, '.drivesync')
store_directory = os.path.join(home, '.gdfl')
if not os.path.exists(store_directory):
    os.makedirs(store_directory)
manifest_directory = os.path.join(store_directory, 'manifest.json')
drive_mount = os.path.expanduser(getYAML(os.path.join(drive_sync_directory, 'config.yml')).get('drive_path'))
pprint = pprint.PrettyPrinter(indent=4).pprint