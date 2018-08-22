import os
import shutil
import pprint
import glob
import hashlib

pprint = pprint.PrettyPrinter(indent=4).pprint

os.chdir(os.getcwd() + '/test')

# files = glob.glob(os.getcwd() + '/**/*.*', recursive=True)
# pprint(files)

# pprint(os.listdir(os.getcwd()))

# ['bla.txt', 'bla2.txt']

# ['bla2.txt', 'reee.txt']

with open('0.txt', 'wb') as f:
    f.fileinfo = {'description': 'this file contains stuff...'}
    f.close()

with open('0.txt', 'wb') as f:
    print(f.fileinfo)
    f.close()


def is_file_modified(file_dict):
    """
    Checks whether a file on the Drive is different from its local counterpart.
    It does this by comparing their hash values.
    :param file_dict: A dictionary containing the details about the file.
     The required keys are 'path' and 'fileId'.
    :type file_dict: dict
    :returns: bool
    """

    # If the file does not exist on the Drive,
    # then return true.
    if not file_exists(fileId):
        return True

    remote_file_hash = file_service.get(
        fileId=fileId, fields="md5Checksum").execute()['md5Checksum']

    local_file_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()

    return local_file_hash != remote_file_hash
