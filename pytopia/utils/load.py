import random
from genericpath import isdir
from os import listdir
from os.path import join

from pytopia.resource.loadSave import loadResource


def loadModels(folder, sort=True, shuffle=False, seed=None, numModels=None):
    '''
    Load all models from all the subfolders of the given folder,
    assuming each subfolder contains saved topic model.
    :param sort: if true, sort subfolders by name
    :param shuffle: if true, shuffle subfolders in random order
    :param numModels: if integer, load only this many models,
        from the start of the subfolder list after sort/shuffle
    :return:
    '''
    subfolders = listSubfolders(folder, sort, shuffle, seed)
    if numModels: subfolders = subfolders[:numModels]
    return [loadResource(subf) for subf in subfolders]

def listSubfolders(folder, sort=True, shuffle=False, seed=None):
    '''
    :param sort: if true, sort subfolders by name
    :param shuffle: if true, shuffle subfolders in random order
    :return: a list of full paths to subfolders of given folder.
    '''
    subfolders = [join(folder, f) for f in listdir(folder) if isdir(join(folder, f))]
    if sort or shuffle: subfolders.sort()
    if shuffle:
        if seed: random.seed(seed)
        random.shuffle(subfolders)
    return subfolders