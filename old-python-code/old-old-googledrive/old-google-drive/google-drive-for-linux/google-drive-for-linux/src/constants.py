import pprint
import os
import time

currentSecondsTime = lambda: int(round(time.time() * 1000))

pprint = pprint.PrettyPrinter(indent=4).pprint

initialCWD = os.getcwd()

# maybe keep folder in?  
nonDownloadableFiles = ['document', 'spreadsheet', 'drawing', 'presentation', 'scriptJson', 'folder']