from src.statics import doRequest, IOHelpers, getMimeType, updateJsonFile, getModifiedDate, isoToUnixTimestamp, loadJSONFile, getIfMimeTypeIsSupported, createJSONFile
from src.constants import pprint, currentSecondsTime
from src.IoOperations import IoOperations
from src.GoogleFile import GoogleFile
from src.Store import store, Reducers
import time
import os
import magic

class DriveSync:
    def __init__(self):
        store.setState({ 
            'driveFiles': [],
            'localFiles': [] 
        })
        self.updateOperationsQueue = []

    def returnDriveFilesInStore(self):
        return store.getState().get('driveFiles')

    def returnLocalFilesInStore(self):
        return store.getState().get('localFiles')

    # since normally we'd use the drive copy as a reference and upload the differences, now just download everything
    def firstRun(self):
        self.getAllDriveFileData()
        # we've collected all the data needed for a sync, now time to compare our local copy 
        # using drive as reference for differences
        self.scanDifferences('firstRun')

    def sync(self):
        # self.getAllDriveFileData()
        self.getAllLocalFileData()
        self.scanDifferences('compare')

    def getLocalFileId(self, localFileName):
        for googleFile in self.returnDriveFilesInStore():
            if googleFile.get('title') == localFileName:
                return googleFile.get('id') 

    def getLocalCreatedDate(self, localFileName):
        for googleFile in self.returnDriveFilesInStore():
            if googleFile.get('title') == localFileName:
                return googleFile.get('createdDate')

    def localFileTemplate(self, name, root, isDirectory=False):
        if len(self.returnDriveFilesInStore()) <= 0:
            raise ValueError('No drive files found to get IDs from')
        path = os.path.join(root, name)
        lastModified = getModifiedDate(path)
        _id = self.getLocalFileId(name)
        pathWithoutDriveDir = path.replace(IOHelpers.googleDriveDirectory, '')
        if len(path) == 0:
            path = IOHelpers.googleDriveDirectory
        if not isDirectory:
            mimeType = magic.from_file(path, mime=True)
        else:
            mimeType = getMimeType('folder')
        _file = {
            'lastModified': lastModified,
            'path': path,
            'id': _id,
            'isDirectory': isDirectory,
            'title': name,
            'mimeType': mimeType,
            # yeah, it'll break in around a few thousand years. we'll all be dead by then, or atleast, i'll be
            'createdDate': 999999999999
        }
        return _file
    def getAllLocalFileData(self):
        localFiles = []
        # since we need to compare filenames to determine which files are in drive and which are not.
        if not self.returnDriveFilesInStore():
            self.getAllDriveFileData()
        for root, dirs, files in os.walk(IOHelpers.googleDriveDirectory, topdown=True):
            # ew! duplicate code!
            # -me, probably
            for name in files:
                localFiles.append(self.localFileTemplate(name, root, False))
            for name in dirs:
                localFiles.append(self.localFileTemplate(name, root, True))
        store.setState({
            'localFiles': localFiles
        })

    def getAllDriveFileData(self):
        filePaths = []
        uri = 'https://www.googleapis.com/drive/v2/files/'
        params = {
            'fields': 'items(id,mimeType,parents,title,modifiedDate,createdDate,labels)'
        }
        driveFiles = (doRequest(uri, params)).get('items')

        for gFile in driveFiles:
            _gFile = GoogleFile(None, gFile, driveFiles)
            if _gFile:
                if getIfMimeTypeIsSupported(_gFile.getRawFile().get('mimeType')):
                    # don't process trashed files
                    if _gFile.getRawFile().get('labels').get('trashed'):
                        continue
                    path = _gFile.getFilePath()
                    # give path root
                    if len(path) == 0:
                        path = ''
                    lastModified = isoToUnixTimestamp(gFile.get('modifiedDate'))
                    _gFile = {
                        'id': gFile.get('id'),
                        'title': gFile.get('title'),
                        'mimeType': gFile.get('mimeType'),
                        'path': path,
                        'lastModified': lastModified,
                        'createdDate': isoToUnixTimestamp(gFile.get('createdDate'))
                        } 
                    filePaths.append(_gFile)
        store.setState({'driveFiles': filePaths})

    def createJob(self, metadata, jobType='', priority=0, justReturnJob=False, excessMetaData=None):
        title = metadata.get('title')
        path = metadata.get('path')
        _id = metadata.get('id')
        mimeType = metadata.get('mimeType')
        # (try to) infer mimeType
        if not mimeType:
            if IOHelpers.exists(path) or IOHelpers.exists(os.path.join(IOHelpers.googleDriveDirectory, path)):
                if os.path.isdir(path):
                    mimeType = getMimeType('folder')
                elif os.path.isfile(path):
                    mimeType = magic.from_file(path, mime=True)
        if mimeType != getMimeType('folder') and path.split('/')[len(path.split('/')) - 1] != title:
            path = os.path.join(path, title)
        job = {
            'title': title,
            'path': path,
            'id': _id,
            'jobType': jobType,
            'priority': priority,
            'mimeType': mimeType
        }
        if excessMetaData:
            job['excessMetaData'] = excessMetaData
        # for _job in self.updateOperationsQueue:
        #     # to avoid duplicates in queue
        #     if job.get('path') == _job.get('path') or os.path.join(IOHelpers.googleDriveDirectory, job.get('path')) == _job.get('path') or os.path.join(IOHelpers.googleDriveDirectory, job.get('path')) == os.path.join(IOHelpers.googleDriveDirectory, _job.get('path')) and job.get('priority') == 0:
        #      
        if justReturnJob:
            return job

        if job and not justReturnJob:
            self.updateOperationsQueue.append(job)
                

    def getIfPathMatch(self, a, b):
        possiblePathOne = os.path.join(IOHelpers.googleDriveDirectory, a.get('path'))
        possiblePathTwo = os.path.join(IOHelpers.googleDriveDirectory, b.get('path'))
        possiblePathThree = os.path.join(possiblePathOne, a.get('title'))
        possiblePathFour = os.path.join(possiblePathTwo, b.get('title'))
        return (
            (a.get('path') == b.get('path') 
            or a.get('path') == possiblePathTwo
            or possiblePathOne == b.get('path') 
            or possiblePathOne == possiblePathTwo
            or possiblePathThree == possiblePathFour
            or a.get('path') == possiblePathFour
            or b.get('path') == possiblePathThree)
            and a.get('title') == b.get('title'))

    def scanDifferences(self, reference):
        localPaths = []
        for root, dirs, files in os.walk(IOHelpers.googleDriveDirectory, topdown=True):
            for name in files:
                lPath = (os.path.join(root,name)).replace(IOHelpers.googleDriveDirectory, '')
                localPaths.append(lPath)
            for name in dirs:
                lPath = (os.path.join(root, name)).replace(IOHelpers.googleDriveDirectory, '')
                localPaths.append(lPath)

        # since first run is explicit there's a special case for first time run.
        if reference == 'firstRun':
            _filePaths = self.returnDriveFilesInStore()
            for filePath in _filePaths:
                # so if the directory doesn't already exist, create it include sub folders(and files)
                _path = os.path.join(IOHelpers.googleDriveDirectory, filePath.get('path'))
                # != folder is because files self don't get a direct path, just that of their parent for using in changing CWD
                if not IOHelpers.exists(_path) or filePath.get('mimeType') != getMimeType('folder'):
                    IoOperations.create(filePath)
            
            # complete! if errors then we already crashed. True in string
            updateJsonFile('json_data/settings.json', { 'fullSync': "True" })
        elif reference == 'compare':
            _localFilePaths = self.returnLocalFilesInStore()
            _filePaths = self.returnDriveFilesInStore()
            lastSyncTime = loadJSONFile('json_data/settings.json').get('lastSyncTime')
            fullSync = bool(loadJSONFile('json_data/settings.json').get('fullSync'))
            self.updateOperationsQueue = []
            googleDriveFilesCopy = _filePaths.copy()
            localFilesCopy = _localFilePaths.copy()

            if fullSync is False:
                raise ValueError("We haven't completed full sync, please delete your google drive directory and let the initial syncing finish before closing the program.")
                return None

            googleDriveFiles = self.returnDriveFilesInStore()
            localFiles = self.returnLocalFilesInStore()
            store = loadJSONFile('json_data/store.json')
            localCache = store.get('localCache')
            googleDriveCache = store.get('googleDriveCache')
            def filterFiles(files, cache, remainderStartPoint, filterType, debug=False):
                _r = remainderStartPoint.copy()
                _c = cache.copy()
                _f = files.copy()

                if debug:
                    pprint('---')
                    pprint('files')
                    pprint(_f)
                    pprint('---')
                    pprint('cache')
                    pprint(_c)
                    pprint('---')
                    pprint('remainder start point')
                    pprint(_r)
                    pprint('---')
                    
                for c in cache:
                    isInFiles = False
                    item = None

                    for x in files:
                        if self.getIfPathMatch(c, x):
                            isInFiles = True
                            item = x

                    if isInFiles:
                        for idx, x in enumerate(_r):
                            if self.getIfPathMatch(x, c) and self.getIfPathMatch(x, item):
                                _r.pop(idx)

                return _r

            
            # filesToRemoveFromDrive = filterFiles(localFiles, localCache, localCache, 'deleteDriveFile')
            # filesToRemoveFromLocal = filterFiles(googleDriveFiles, googleDriveCache, googleDriveCache, 'deleteLocalFile')

            # download entire drive
            # download new revisions from drive or upload new revisions
            filesToDownload = filterFiles(googleDriveFiles, localFiles, googleDriveFiles, 'downloadFromDrive')
            filesToUpload = filterFiles(localFiles, googleDriveFiles, localFiles, 'uploadToDrive')
            
            # download new copy of file to local from drive
            for googleDriveFile in googleDriveFiles:
                if googleDriveFile.get('lastModified') > lastSyncTime and getIfMimeTypeIsSupported(googleDriveFile.get('mimeType')):
                    self.createJob(googleDriveFile, 'localFileUpdate')
                
            # upload new copy of file to drive from local
            for localFile in localFiles:
                if localFile.get('lastModified') > lastSyncTime and getIfMimeTypeIsSupported(localFile.get('mimeType')):
                    self.createJob(localFile, 'driveFileUpdate')
            
            def addToQueue(files, jobType, priority=0):
                for f in files:
                    self.createJob(f, jobType, priority)

            # addToQueue(filesToRemoveFromDrive, 'deleteDriveFile', 2)
            # addToQueue(filesToRemoveFromLocal, 'deleteLocalFile', 2)
            addToQueue(filesToDownload, 'downloadFromDrive', 1)
            addToQueue(filesToUpload, 'uploadToDrive', 1)

            # jobs with priority 1 go first
            for idx, _job in enumerate(self.updateOperationsQueue):
                for _job2 in self.updateOperationsQueue:
                    def jobCheck(a, b, prio1, prio2):
                        return a == prio1 and b == prio2
                    if self.getIfPathMatch(_job, _job2):
                        # and int(_job2.get('priority')) == 1 and int(_job.get('priority')) == 0
                        if jobCheck(_job2.get('priority'), _job.get('priority'), 2, 1):
                            self.updateOperationsQueue.pop(idx) 
                        elif jobCheck(_job2.get('priority'), _job.get('priority'), 1, 0):
                            self.updateOperationsQueue.pop(idx) 

            pprint('update queue')

            pprint(self.updateOperationsQueue)

            for x in self.updateOperationsQueue:
                IoOperations.handleJob(x)

        self.saveCache()

    def cacheFormatter(self, data):
        _r = []
        for x in data:
            _r.append({
                'id': x.get('id'),
                'title': x.get('title'),
                'path': x.get('path'),
                'mimeType': x.get('mimeType')
            })
        return _r

    def saveLocalCache(self):
        updateJsonFile('json_data/store.json', { 'localCache': self.cacheFormatter(self.returnLocalFilesInStore()) }) 

    def saveGoogleDriveCache(self):
        updateJsonFile('json_data/store.json', { 'googleDriveCache': self.cacheFormatter(self.returnDriveFilesInStore()) })

    def saveCache(self, saveType='all'):
        store.setState({
            'driveFiles': [],
            'localFiles': [],
        })
        # refresh current file data since the files could have been changed with the sync
        self.getAllLocalFileData()
        nowTimeInSeconds = currentSecondsTime() / 1000
        # add 5 seconds to last sync time for modified checks (update/download)
        # nowTimeInSeconds = nowTimeInSeconds + 5

        if saveType == 'all':
            self.saveLocalCache()
            self.saveGoogleDriveCache()
        elif saveType == 'local':
            self.saveLocalCache()
        elif saveType == 'drive':
            self.googleDriveDirectory()

        updateJsonFile('json_data/settings.json', { 'lastSyncTime': int(nowTimeInSeconds) })  


        

        
        