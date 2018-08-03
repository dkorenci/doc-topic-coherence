import os
from os import path

class FolderLocation():

    def __init__(self, folder):
        self.rootFolder = folder

    def subfolder(self, *folders):
        '''
        Legacy method, __getitem__ should be used as it is more general.
        :param folders: relative path from root folder
        :return: return full path, if needed create all the subfolders
        '''
        fullpath = path.join(self.rootFolder, *folders)
        #path.isdir
        if not path.exists(fullpath):
            os.makedirs(fullpath, mode=0770)
        return fullpath

    def __call__(self, *path_):
        '''
        Return full path created by appending path_ to rootFolder.
        *path_ is path.join()-ed with rootFolder, if the last member
         of the path is/should be a folder it must end with '/'
        Create all the folders in the full path if they don't exist.
        If the path ends in a file, it is not created.
        :param path: list of strings describing relative paths,
            last path can be a file path
        :return:
        '''
        fullpath = path.join(self.rootFolder, *path_)
        pathf = path.dirname(fullpath)
        if not path.exists(pathf):
            os.makedirs(pathf, mode=0770)
        return fullpath
