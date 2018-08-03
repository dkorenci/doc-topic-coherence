'''
Methods for loading/saving a resource from/to a folder.
Each save-able resource has to provide save and load instance methods
 that accept a folder as a parameter.
For saving, resource.save(folder) is called.
For loading from folder, first resource is depickled from a
 predefined file withing the folder and than, resource.load(folder)
 is called on depickeld instance, if load method is defined for the object.
 In this way non-pickleable data can be loaded from the folder.
'''

import cPickle, os
from os import path

objectSaveFile = 'object.pickle'

__rescache = None
def resourceCache():
    global __rescache
    if __rescache is None: __rescache = {}
    return __rescache

def loadResource(folder, objectFile=objectSaveFile, cache=False):
    '''
    Load and return a resource saved in the specified folder.
    :param objectFile: name of the file containing pickled resource object
    :param cache: if True, check if resource is in the cache and put resource
            the cache and upon loading, use global cache
    '''
    folder = path.abspath(folder)
    if cache:
        rescache = resourceCache()
        if folder in rescache: return rescache[folder]
    res = cPickle.load(open(path.join(folder, objectFile), 'rb'))
    if hasattr(res, 'load') and callable(getattr(res, 'load')):
        res.load(folder)
    if cache: rescache[folder] = res
    return res

def saveResource(res, folder):
    '''Save an resource to the folder. '''
    res.save(folder)

def pickleObject(obj, folder, objectFile=objectSaveFile):
    '''Pickle object to folder/objectSaveFile, creating the folder if does not exist.'''
    if not path.exists(folder): os.makedirs(folder)
    cPickle.dump(obj, open(path.join(folder, objectFile), 'wb'))
