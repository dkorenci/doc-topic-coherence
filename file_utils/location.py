'''
Configures utility classes from project settings.
'''

import os, random
from os import path, listdir
from os.path import join
from genericpath import isdir, isfile

class FolderLocation():

    def __init__(self, folder):
        self._root = folder

    def __str__(self): return self._root

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
        fullpath = path.join(self._root, *path_)
        pathf = path.dirname(fullpath)
        if not path.exists(pathf):
            os.makedirs(pathf, mode=0770)
        return fullpath

    def subfolders(self, sort=True, shuffle=False, seed=0, abspath=True):
        '''
        Return the list of locations's subfolders
        :param sort: if true, sort subfolders by name
        :param shuffle: if true, shuffle subfolders in random order
        :return: a list of full paths to subfolders of given folder.
        '''
        folder = lambda f: join(self._root, f) if abspath else f
        subfolders = [folder(f) for f in listdir(self._root)
                        if isdir(join(self._root, f))]
        if sort or shuffle: self.__sortShuffle(subfolders, shuffle, seed)
        return subfolders

    def files(self, sort=True, shuffle=False, seed=0):
        '''
        Return list of files in the location folder.
        '''
        files = [join(self._root, f) for f in listdir(self._root)
                      if isfile(join(self._root, f))]
        if sort or shuffle: self.__sortShuffle(files, shuffle, seed)
        return files

    def __sortShuffle(self, l, shuffle, seed=0):
        '''Sort and optionally shuffle list in place '''
        l.sort()
        if shuffle:
            random.seed(seed)
            random.shuffle(l)

if __name__ == '__main__':
    pass