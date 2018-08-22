import json
import os
import pathlib
import requests
import shutil
from src.constants import pprint, initialCWD, nonDownloadableFiles
from datetime import datetime
from src.Store import store
# from src.IoOperations import IoOperations

def loadJSONFile(fileName):
    os.chdir(initialCWD)
    if os.path.exists(fileName):
        with open(fileName) as f:
                return json.load(f)
    else:
        return False

def createJSONFile(fileDir, payload):
    # to be sure we're in the correct cwd (the module dir)
    os.chdir(initialCWD)
    data = {}
    for key, value in payload.items():
        data[key] = value

    jsonFile = open(fileDir, "w+")
    jsonFile.write(json.dumps(data))
    jsonFile.close()

def isoToUnixTimestamp(isoDate):
    utc_dt = datetime.strptime(isoDate, '%Y-%m-%dT%H:%M:%S.%fZ')
    timestamp = (utc_dt - datetime(1970, 1, 1)).total_seconds()
    return int(timestamp)

def updateJsonFile(fileName, payload):
    # to be sure we're in the correct cwd (the module dir)
    os.chdir(initialCWD)

    jsonFile = open(fileName, "r") # Open the JSON file for reading
    data = json.load(jsonFile) # Read the JSON into the buffer
    jsonFile.close() # Close the JSON file

    for key, value in payload.items():
        data[key] = value

    jsonFile = open(fileName, "w+")
    jsonFile.write(json.dumps(data))
    jsonFile.close()

def getModifiedDate(filePath):
    return int(os.path.getmtime(filePath))

def getMimeType(mimeType):
    return JSONData.mimeTypes.get(mimeType)

def doRequest(url=None, params={}, requestType='get', parseAsJson=True, metadata=None):
    token = JSONData.token
    headers = {'Authorization': 'Bearer ' + token}
    def checkForError(request):
        if request.status_code >= 400:
            pprint('--- DO REQUEST ERROR ---')
            pprint(request.text)
            # pprint(request.json())    
            pprint(request.url)
            pprint(url)
            pprint(metadata)
            pprint('--- END ---')
    if requestType == 'get' and url and token:
        r = requests.get(url, headers=headers, stream=True, params=params)
        checkForError(r)
        if parseAsJson:
            return r.json()
        else:
            return r
    elif requestType == 'post' and url and token:
        if metadata:
            if metadata.get('files'):
                r = requests.post(url, headers=headers, files=metadata.get('files'))
                checkForError(r)
                return r
        r = requests.post(url, headers=headers)
        checkForError(r)
        return r
    elif requestType == 'put' and url and token:
        r = requests.put(url, headers=headers, files=metadata.get('files'))
        checkForError(r)
        return r


def downloadFile(url, filePath, mimeType):
    # path = os.path.join(IOHelpers.googleDriveDirectory, filePath)
    # pathSplitted = path.split('/')
    # fileName = pathSplitted[len(pathSplitted) - 1]
    # # path.pop()
    # # path = '/'.join(path)
    # # since if a file is at root the root '/' is removed by the .split
    # if len(path) == 0:
    #     path = IOHelpers.googleDriveDirectory
    # # remove file if exists
    # if IOHelpers.exists(path):
    #     if os.path.isdir(path):
    #         shutil.rmtree(path)
    #     if os.path.isfile(path):
    #         os.unlink(path)
    # # make parent folders, if exists just skip creating
    # pathSplittedCopy = pathSplitted.copy()
    # pathSplittedCopy.pop()
    if os.path.isfile(filePath):
        print('making dirs')
        os.makedirs(filePath, exist_ok=True)
    elif os.path.isdir(filePath):
        print('making dirs2')
        os.makedirs(filePath, exist_ok=True)
    elif not IOHelpers.exists(filePath) and mimeType != getMimeType('folder'):
        print('making dirs3')
        print(mimeType)
        # since path is absolute to file pop last file
        splitted = filePath.split('/')
        splitted.pop()
        newPath = '/'.join(splitted)
        os.makedirs(newPath, exist_ok=True)
    r = doRequest(url, {}, 'get', False)
    with open(os.path.join(filePath), 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return True

def testIfParentsExist():
    pass

# TODO add folder to upload file as well, in base upload job, so empty directories also get uploaded
def uploadFile(url, filePath, job, uploadType='upload'):
    filePathFromDriveRoot = filePath.replace(IOHelpers.googleDriveDirectory, '')

    if os.path.isdir(filePath):
        # ignore empty folder uploads 
        return None
    # make sure all the parent folders are in drive, if not, insert them
    queue = store.getState().get('driveFiles')
    pprint(queue)
    # for g in driveFiles:
    #     for idx, x in enumerate(queue):
    #         if x.get('id') != None and x.get('id'):
    #             pass


    para = {
        "title": job.get('title'),
        # TODO implement nested file upload
        # "parents": [{"id": "root"}]
    }
    files = {
        "data": ("metadata", json.dumps(para), "application/json; charset=UTF-8"),
        "file": open(filePath, 'rb')
    }

    metadata = {
        "files": files
    }
    if uploadType == 'upload':
        doRequest(url, {}, 'post', False, metadata)
    elif uploadType == 'update':
        doRequest(url, {}, 'put', False, metadata)

class JSONData:
    token = loadJSONFile('json_data/token.json').get('access_token') if os.path.exists(os.path.join(os.getcwd(), 'json_data/token.json')) else None
    credentials = loadJSONFile('json_data/credentials.json')
    mimeTypes = loadJSONFile('json_data/googleMIMETypes.json')
    settings = loadJSONFile('json_data/settings.json')

    @staticmethod
    def getToken():
        return loadJSONFile('json_data/token.json').get('access_token') if os.path.exists(os.path.join(os.getcwd(), 'json_data/token.json')) else None

    def refresh(self):
        os.chdir(initialCWD)
        JSONData.token = JSONData.getToken()
        JSONData.credentials = loadJSONFile('json_data/credentials.json') or None
        JSONData.mimeTypes = loadJSONFile('json_data/googleMIMETypes.json') or None
        JSONData.settings = loadJSONFile('json_data/settings.json') or None
    
class IOHelpers:
    oldCWD = os.getcwd()
    googleDriveDirectory = JSONData.settings.get('directory')
    
    def checkIfDriveDirectoryExists(self):
        if IOHelpers.exists(IOHelpers.googleDriveDirectory) is False:
            os.mkdir(IOHelpers.googleDriveDirectory)
            return True
        return False

    @staticmethod
    def changeCwd(dir):
        os.chdir(dir)

    @staticmethod
    def getCwd(self):
        return os.getcwd()

    @staticmethod
    def changeCwdToGoogleDriveDirectory():
        os.chdir(self.googleDriveDirectory)
    
    @staticmethod
    def changeCwdToOldDirectory(self):
        os.chdir(self.oldCwd)

    @staticmethod
    def exists(absolutePathToFile):
        path = pathlib.Path(absolutePathToFile)
        return path.is_dir() or path.is_file()

def getIfMimeTypeIsSupported(mimeType):
    return mimeType not in { key: JSONData.mimeTypes[key] for key in nonDownloadableFiles}.values()