import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pprint

pprint = pprint.PrettyPrinter(indent=4).pprint

class Watcher:
    DIRECTORY_TO_WATCH = "/home/thomas/gitrepos/google-drive-for-linux/test"

    def __init__(self):
        
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


if __name__ == '__main__':
    w = Watcher()
    w.run()