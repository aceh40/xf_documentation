import settings
import os
from logger import logger


path = settings.TARGET_ROOT_DIR

def file_scanner():
    """ Return the list of all files and folders in Xpressfeed directory.
    """
    for root, dirs, files in os.walk(path):
        print(path)
        print(root)
        print(dirs)
        print(files)
        return root, dirs, files

file_scanner()

