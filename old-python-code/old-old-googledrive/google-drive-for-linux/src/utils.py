import subprocess

def spawn_subprocess(x):
    process = subprocess.Popen(x, stdout=subprocess.PIPE)
    out, err = process.communicate()
    if err:
        raise Exception(err)
    return out

def check_if_installed(cmd, args, errMessage):
    process = subprocess.Popen([cmd, args], stdout=subprocess.PIPE)
    out, err = process.communicate()
    if err:
        raise Exception(errMessage if errMessage else err)
    else:
        return out
