from src.statics import doRequest, getMimeType
import urllib.parse
from src.constants import pprint

class GoogleFile:
    def __init__(self, id=None, data=None, driveFiles=None):
        if id:
            uri = 'https://www.googleapis.com/drive/v2/files/' + id
            params = {
                'fields': 'id,mimeType,parents,title,modifiedDate,createdDate,labels'
            }
            self.file = doRequest(uri, params)
        elif data and id is None:
            self.file = data
        self.driveFiles = driveFiles
        self.path = []

    def getParents(self):
        return self.file['parents']

    def updateRawFile(self, key, value):
        self.file[key] = value

    # zoek parent id in all files, kijk naar parent id van die etc etc

    def getFurtherParents(self, id, path):
        for idx, driveFile in enumerate(self.driveFiles):
            if driveFile.get('id') == id: 
                path.append(driveFile.get('title'))
                if len(driveFile.get('parents')) > 0:
                    return self.getFurtherParents(driveFile.get('parents')[0].get('id'), path)
                else:
                    return path

    def _getFilePath(self, id, path):
        # keep recursion up
        if len(self.getRawFile().get('parents')) > 0:
            parentId = self.file.get('parents')[0].get('id')
            for idx, driveFile in enumerate(self.driveFiles):
                if driveFile.get('id') == parentId:
                    if len(driveFile.get('parents')) > 0:
                        return self.getFurtherParents(driveFile.get('parents')[0].get('id'), [driveFile.get('title')])
                    else:
                        return [driveFile.get('title')]

            # for idx, driveFile in enumerate(self.driveFiles):
            #     for idx2, driveFile2 in enumerate(self.driveFiles):

            #     if driveFile.get('id') == parent.get('id'):
            #         if len(driveFile.get('parents')) > 0:
            #             path.append(driveFile.get('title'))
            #             return self._getFilePath(driveFile.get('parents')[0].get('id'), path)
        # end recursion and return
        else:
            return path

    def getAllParentTitles(self, gFile, titles):
        if len(gFile.get('parents')) > 0 and gFile.get('parents')[0].get('isRoot') != True:
            parentId = gFile.get('parents')[0].get('id')
            for b in self.driveFiles:
                if b.get('id') == parentId:
                    titles.append(b.get('title'))
                    return self.getAllParentTitles(b, titles)
        else:
            return titles

    def getFilePath(self):
        try:
            if len(self.file['parents']) <= 0:
                return ''
                
            gFilePath = self.getAllParentTitles(self.file, [])
            gFilePath.reverse()
            if self.file['mimeType'] == getMimeType('folder'):
                gFilePath.append(self.file['title'])
            pprint(gFilePath)
            return '/'.join(gFilePath)

            # pprint(self.driveFiles)


            # _arr = self._getFilePath(, _path)
            # pprint(_arr)
            # _arr.reverse()
            # _arr.pop(0)
            
            # if not onlyFolders:
                # _arr.append(self.file['title'])
            # return '/'.join(_arr)
        except expression as identifier:
            pass
        
        # path2 = path
        # parents = self.file['parents']
        # if len(parents) > 0:
        #     parentId = parents[0].get('id')
        #     path2.append(GoogleFile(parentId).getFilePath(path2))
        # if len(parents) <= 0:
        #     return path2
        # return self.file['title']

    def getRawFile(self):
        return self.file

    def getChildren(self):
        uri = 'https://www.googleapis.com/drive/v2/files/' + self.file.get('id') + '/children'
        params = {
            'fields': 'items'
        }
        res = doRequest(uri, params)
        children = res.get('items')

        return children