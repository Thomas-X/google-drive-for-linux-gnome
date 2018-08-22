import subprocess
import os
import yaml
import json

def spawn_subprocess(x, return_sub_process=False, noPipe=False):
    output = subprocess.check_output(x)
    return output

def check_if_installed(cmd, args, errMessage):
    process = subprocess.Popen([cmd, args], stdout=subprocess.PIPE)
    out, err = process.communicate()
    if err:
        raise Exception(errMessage if errMessage else err)
    else:
        return out

def getModifiedDate(filePath):
    return int(os.path.getmtime(filePath))

def getYAML(path):
    with open (os.path.join(path), 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

class JSON:
    @staticmethod
    def createJSONFile(fileDir, payload):
        data = {}
        for key, value in payload.items():
            data[key] = value

        jsonFile = open(fileDir, "w+")
        jsonFile.write(json.dumps(data))
        jsonFile.close()

    @staticmethod
    def updateJsonFile(fileDir, payload):
        jsonFile = open(fileDir, "r")
        data = json.load(jsonFile) 
        jsonFile.close() 

        for key, value in payload.items():
            data[key] = value

        jsonFile = open(fileDir, "w+")
        jsonFile.write(json.dumps(data))
        jsonFile.close()

    @staticmethod
    def loadJSONFile(fileDir):
        if os.path.exists(fileDir):
            with open(fileDir) as f:
                    return json.load(f)
        else:
            JSON.createJSONFile(fileDir, {})
    