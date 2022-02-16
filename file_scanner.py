import settings
import os
from logger import logger

path = r''

def file_scanner(path):
    """ Return the list of all files and folders in Xpressfeed directory.
    """
    # file_list = []
    file_dict = {}
    for root, dirs, files in os.walk(path):
        for file in files:
            # file_list.append([root, file])
            file_dict[file] = root
    return file_dict


file_dict = file_scanner(path)

# for key in file_dict.keys():
#     print(key + ' >>> ' + file_dict[key])
# print (len(file_dict))
