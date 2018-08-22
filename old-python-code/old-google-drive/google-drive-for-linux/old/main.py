#!/usr/bin/env python
from __future__ import print_function
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import pprint
import requests
import json
import os
import pathlib

# [] - settings.json met google drive directory
# [] - log 'sync' date
# [] - alleen bepaalde folders downloaden
# [] - DB integration

# hou een lijst bij met alle bestanden en de paths van die bestanden
# als bestand niet meer bestaat, delete bestand vanuit Drive en update lijst met alle bestanden,
# upload bestanden die nieuw zijn (dus gerenamed). 

## V1.1 rewrite plan ##

## Drive functions ##
# - delete file
# - upload file
# - update file
# - give file structure

## Base functions ##
# - download file
# - delete file
# - upload file
# - update file
# - give local file structure
# - compare files (op basis van lokale kopie)

## Startup ##
# - check of googledrive directory bestaat, zo niet, doe full sync
# - als google drive directory wel bestaat (dit is dus de sync): 
    # - pak alle bestanden en paths (via os.listdir) van googledrive directory
    # - pak alle bestanden en paths van drive
    # - vergelijk op basis van lokale bestanden, als er een bestand is die niet in drive staat, upload
    # - als er een bestand is die wel in drive staat maar niet lokaal, verwijder uit drive
    # - tot de lokale kopie van google drive gelijk is aan die van online
    
# https://github.com/Anmol-Singh-Jaggi/gDrive-auto-sync/blob/master/gDrive-auto-sync/upload.py

pprint = pprint.PrettyPrinter(indent=4).pprint
## TODO IO stuff, creating folder if type is folder, downloading if type is else than supported mimetypes

class IOHandler:
    def __init__(self, settings):
        self.oldCwd = os.getcwd()
        self.currentCwd = os.getcwd()
        googleDriveDirectory = settings.get('directory')
        if self.exists(googleDriveDirectory) is False:
            os.mkdir(googleDriveDirectory)
        self.googleDriveDirectory = googleDriveDirectory 
        pass

    def changeCwd(self, dir):
        os.chdir(dir)

    def getCwd(self):
        return os.getcwd()

    def changeCwdToGoogleDriveDirectory(self):
        os.chdir(self.googleDriveDirectory)
    
    def changeCwdToOldDirectory(self):
        os.chdir(self.oldCwd)

    def exists(self, absolutePathToFile):
        path = pathlib.Path(absolutePathToFile)
        return path.is_dir() or path.is_file()

    @staticmethod
    def loadFile(fileName):
        with open(fileName) as f:
            return json.load(f)

    def createFolder(self, name):
        os.mkdir(name)
    
    def removeFile(self, name):
        pass

    def createFile(self, name):
        os.mkdir(name)
    
    # for syncing new files use /tmp, so download new files to /tmp/google-drive-for-linux
    # and move them to old file directory
    def updateFile(self, newFileDirectory, newFileName, oldFileDirectory):
        pass

# load files
# settings = IOHandler.loadFile('settings.json')
# mimeTypes = IOHandler.loadFile('googleMIMETypes.json')
# token = IOHandler.loadFile('token.json')

class GoogleDrive:
    def __init__(self):
        self.settings = IOHandler.loadFile('settings.json')
        self.ioHandler = IOHandler(self.settings)
        self.mimeTypes = IOHandler.loadFile('googleMIMETypes.json')
        GoogleDrive.mimeTypes = self.mimeTypes
        GoogleDrive.getMimeType = self.getMimeType
        self.ioHandler = IOHandler(self.settings)
        self.syncQueue = []

        SCOPES = 'https://www.googleapis.com/auth/drive'
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)

        self.token = creds.access_token
        self.service = build('drive', 'v3', http=creds.authorize(Http()))
        # results = service.files().list(
        #     pageSize=10, fields="nextPageToken, files(id, name)").execute()
        # items = results.get('files', [])
        # if not items:
        #     print('No files found.')
        # else:
        #     print('Files:')
        #     for item in items:
        #         print('{0} ({1})'.format(item['name'], item['id']))

    @staticmethod
    def doRequest(url=None, requestType='get', token=None):
        if requestType == 'get' and url and token:
            headers = {'Authorization': 'Bearer ' + token}
            return requests.get(url, headers=headers, stream=True)

    def getToRoot(self, id):
        gFileParents = GoogleFile(id, self.token).getParents()
        if len(gFileParents) > 0:
            return self.getToRoot(GoogleFile(id, self.token).getParents()[0].get('id'))
        else:
            self.ioHandler.changeCwdToGoogleDriveDirectory()
            return GoogleFile(id, self.token).getChildren(['mimeType', 'title', 'id', 'parents'], self.ioHandler.getCwd())

    def getMimeType(self, type):
        return self.mimeTypes.get(type)

    # Er zijn twee types sync
    # 1 - sync vanuit de gdrive cloud
    # 2 - sync vanuit lokale changes, deze moet als eerst gerunt worden

    def ioOperations(self, child):
        unsupportedTypes = ['document', 'spreadsheet', 'drawing', 'presentation', 'scriptJson', 'folder']
        if child.get('cwd') and child.get('mimeType') == self.getMimeType('folder'):
            _arr = child.get('cwd').split('/')
            # 0 index is empty string, since path begins with /, so remove
            del _arr[0]
            _arr.pop()
            _CWD = '/' + os.path.join('/'.join(_arr))
            self.ioHandler.changeCwd(_CWD)
        
        if child.get('cwd') and child.get('mimeType') != self.getMimeType('folder'):
            self.ioHandler.changeCwd(child.get('cwd'))

        if child.get('mimeType') == self.getMimeType('folder'):
            self.ioHandler.createFolder(child.get('title'))
            for subChild in child.get('children'):
                
                if subChild.get('mimeType') == self.getMimeType('folder'):
                    self.syncFromCloud(subChild.get('children'), subChild)
                else:
                    self.ioOperations(subChild)

        # god I love python.
        # checks if mimeType is not in the unsupported (non downloadable) files types with dict comprehension
        if child.get('mimeType') not in { key: self.mimeTypes[key] for key in unsupportedTypes}.values():
            uri = 'https://www.googleapis.com/drive/v3/files/' + child.get('id') + '?alt=media'
            self.downloadFile(uri, child.get('title'), child.get('mimeType'))
            

        # TODO implement all google suite types with .gdoc and just open browser
        # in google drive if clicked on (open with google drive sync)
        # basically some metadata should be in the .gdoc file but nothing else
        # since its just a href to a browser    
        # elif child.get('mimeType') == self.getMimeType('document'):
        #     pprint('yeaaa')
        #     pprint(child)
        #     self.ioHandler.createFile(child.get('title') + '.txt')
        # elif child.get('mimeType') == self.getMimeType('spreadsheet'):
        #     pass

    def syncFromCloud(self, children, rootFolderOfChildren=None):
        if rootFolderOfChildren:
            self.ioOperations(rootFolderOfChildren)
        for child in children:
            self.ioOperations(child)

            

    def sync(self, rootChildren):
        self.syncFromCloud(rootChildren)
        # self.recursiveSync(rootChildren, True)
        # TODO make getAllFiles / baseRoutine / sync one function
        
        
    def baseRoutine(self):
        # to get hierachy, go to top-level and work down from there
        gFile = GoogleFile(self.files[0]['id'], self.token)
        rootChildren = self.getToRoot(gFile.getParents()[0].get('id'))
        self.sync(rootChildren)
        # self.getParents(firstFile['id'])

        # for file in self.files:
        #     pprint(file)
        # download / upload / check for updates here

    def getAllFiles(self):
        gFiles = self.service.files()
        gList = gFiles.list()
        files = gList.execute().get('files', [])
        self.files = files
        self.baseRoutine()

        # for item in results:
        #     uri = 'https://www.googleapis.com/drive/v2/files/' + item['id'] + '?fields=children'
            
        #     data = self.doRequest(uri).json()
        #     pprint(data)

        #     if item['mimeType'] is not 'application/vnd.google-apps.folder':
        #         stri = 'https://www.googleapis.com/drive/v3/files/' + item['id'] + '?alt=media'
        #         pprint(stri)
        #         self.download_file(stri)

    # def getChanges(self):
        # get revisions and compare with last sync time

    def downloadFile(self, url, name, mimeType):
        # local_filename = url.split('/')[-1]
        r = GoogleDrive.doRequest(url, 'get', self.token)
        with open(name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
        return True

class GoogleFile:
    def __init__(self, id, token):
        self.token = token
        uri = 'https://www.googleapis.com/drive/v2/files/' + id
        self.file = GoogleDrive.doRequest(uri, 'get', self.token).json()
    
    def getParents(self):
        return self.file['parents']
        
    def updateRawFile(self, key, value):
        self.file[key] = value

    def getRawFile(self):
        return self.file

    def getChildren(self, extraData, currentWorkingDirectory):
        # TODO add ?fields=children to reduce network traffic (and increase performance)
        uri = 'https://www.googleapis.com/drive/v2/files/' + self.file['id'] + '/children'
        res = GoogleDrive.doRequest(uri, 'get', self.token).json()

        children = res.get('items')
        children2 = []
        if len(extraData) >= 0:
            # add children key to allowed keys in sub documents

            for child in children:
                child = GoogleFile(child.get('id'), self.token)
                if child.getRawFile().get('mimeType') == GoogleDrive.getMimeType('folder'):
                    CWD = os.path.join(currentWorkingDirectory, child.getRawFile().get('title')) 
                    childrenOfChilds = child.getChildren(extraData, CWD)
                    child.updateRawFile('children', childrenOfChilds)
                    child.updateRawFile('cwd', CWD)
                    if 'children' not in extraData:
                        extraData.append('children')
                    if 'cwd' not in extraData:
                        extraData.append('cwd')

                child = child.getRawFile()
                # only include certain keys if extraData len > 0
                if len(extraData) > 0:
                    child = { key: child[key] for key in extraData }
                    if 'children' in extraData:
                        extraData.remove('children')
                    if 'cwd' in extraData:
                        extraData.remove('cwd')

                if child.get('cwd') is None:
                    child['cwd'] = currentWorkingDirectory

                children2.append(child)

        if len(children2) > 0:
            children = children2

        return children        

gd = GoogleDrive()
gd.getAllFiles()

# class Main:
#     def __init__(self):
#         self.gladefile = "ui.glade"
#         self.builder = Gtk.Builder()
#         self.builder.add_from_file(self.gladefile)
#         self.builder.connect_signals(self)
#         self.window = self.builder.get_object("window1")
#         self.window.show()

# if __name__ == "__main__":
#   main = Main()
#   Gtk.main()