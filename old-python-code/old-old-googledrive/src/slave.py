import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pprint
import yaml
import os
from pathlib import Path
home = str(Path.home())

pprint = pprint.PrettyPrinter(indent=4).pprint

class Watcher:
    drive_sync_directory = os.path.join(home, '.drivesync')
    
    def getYAML(self):
        with open (os.path.join(self.drive_sync_directory, 'config.yml'), 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def __init__(self):
        print('HELLO :)')
        yml = self.getYAML()
        drive_path = os.path.expanduser(yml.get('drive_path'))
        self.DIRECTORY_TO_WATCH = drive_path
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            pprint('created')
            pprint(event)

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.=
            pprint('modified')
            pprint(event)

w = Watcher()
w.run()