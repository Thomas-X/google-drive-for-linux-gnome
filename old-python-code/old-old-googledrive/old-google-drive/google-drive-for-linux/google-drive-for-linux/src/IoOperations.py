from src.statics import getMimeType, IOHelpers, downloadFile, JSONData, getIfMimeTypeIsSupported, uploadFile, doRequest
from src.constants import pprint, nonDownloadableFiles
import os
import requests
from src.Auth import Auth
from src.GoogleFile import GoogleFile
import magic
import shutil

class IoOperations:

    # @staticmethod
    # def parseAndExecuteUpdateQueue(queue):
    #     queueOnlyParentFolders = []

    #     # if is a directory then get all 

    #     for item in queue:
    #         # if is directory
    #         if os.path.isdir(item.get('path')):
                
    @staticmethod
    def handleJob(job):
        if job.get('jobType') == 'downloadFromDrive':
            IoOperations.download(job)
        elif job.get('jobType') == 'uploadToDrive':
            IoOperations.upload(job)
        elif job.get('jobType') == 'deleteDriveFile':
            IoOperations.deleteDrive(job)
        elif job.get('jobType') == 'deleteLocalFile':
            IoOperations.deleteLocal(job)
        elif job.get('jobType') == 'driveFileUpdate':
            # if os.path.isfile(job.get('path')):
            IoOperations.update(job)
        elif job.get('jobType') == 'localFileUpdate':
            if os.path.isdir(job.get('path')):
                os.makedirs(job.get('path'))
            else:
                IoOperations.download(job)

    @staticmethod
    def update(job):
        pprint('UPDATE')
        pprint('UPDATE')
        pprint('UPDATE')
        pprint(job)
        pprint('UPDATE')
        pprint('UPDATE')
        pprint('UPDATE')
        
        
        uri = 'https://www.googleapis.com/upload/drive/v2/files/%s?uploadType=multipart' % (job.get('id'))
        uploadFile(uri, job.get('path'), job, uploadType='update')

    @staticmethod
    def download(job):
        path = os.path.join(IOHelpers.googleDriveDirectory, job.get('path')) 
        uri = 'https://www.googleapis.com/drive/v3/files/' + job.get('id') + '?alt=media'
        downloadFile(uri, path, job.get('mimeType'))

    @staticmethod
    def upload(job):
        uri = 'https://www.googleapis.com/upload/drive/v2/files?uploadType=multipart'
        uploadFile(uri, job.get('path'), job)

    @staticmethod
    def deleteDrive(job):
        uri = "https://www.googleapis.com/drive/v2/files/%s/trash" % (job.get('id'))
        r = doRequest(uri, {}, 'post')

    @staticmethod
    def deleteLocal(job):
        # make path absolute
        # isADirectory = self.isDirectory(job.get('path'))
        # might get away with this TODO
        if job.get('title'):
            path = os.path.join(job.get('path'), job.get('title'))
        else:
            path = job.get('path')
        # path = os.path.join(job.get('path'), job.get('title')) if self.isDirectory(job.get('path'), job.get('title')) else 
        if os.path.isdir(path):
            # to avoid removing the entire google drive folder if a file is in the root of google drive folder :)
            if path != IOHelpers.googleDriveDirectory or path != '/':
                shutil.rmtree(path)
            return
        elif IOHelpers.exists(path) and os.path.isfile(path):
            os.unlink(path)
            return
    
    @staticmethod
    def isDirectory(path, title):
        def checkCondition(paths):
            return os.path.isdir(os.path.join(paths))

        if checkCondition([IOHelpers.googleDriveDirectory, path, title]) or checkCondition([path]) or checkCondition([path, title]) or checkCondition([IOHelpers.googleDriveDirectory, path]):
            return True
        else:
            return False

    @staticmethod
    def create(gFile):
        gDriveDir = IOHelpers.googleDriveDirectory
        # types that can't be downloaded since they should be converted
        # TODO add support for these files
        pprint(gFile)
        
        # if its not a folder, we need to change the cwd 
        if gFile.get('mimeType') != getMimeType('folder'):
            _path = os.path.join(gDriveDir, gFile.get('path'))
            os.makedirs(_path, exist_ok=True)
            os.chdir(_path)
        if gFile.get('mimeType') == getMimeType('folder'):
            os.makedirs(os.path.join(gDriveDir, gFile.get('path')))
        if getIfMimeTypeIsSupported(gFile.get('mimeType')):
            uri = 'https://www.googleapis.com/drive/v3/files/' + gFile.get('id') + '?alt=media'
            downloadFile(uri, gFile.get('title'), gFile.get('mimeType'))
        pass

    # create
    # onDelete
    # onCreate