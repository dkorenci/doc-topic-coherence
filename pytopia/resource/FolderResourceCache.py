from pytopia.resource.loadSave import loadResource, saveResource
from logging_utils.setup import *
from logging_utils.tools import fullClassName

from os import path

class FolderResourceCache():
    '''
    Cache for the resource builder, storing built resources in subfolders of a folder.
    Obsolete, use ResourceBuilderCache instead.
    '''

    def __init__(self, builder, folder, id=None, memCache=True):
        '''
        :param memCache: if True, also cache built/loaded object in memory
        '''
        self.__builder = builder
        self.__folder = folder
        self.__log = createLogger(fullClassName(self), INFO)
        self.id = id
        self.__memCache = memCache
        if memCache: self.__cache = {}

    def __call__(self, *args, **kwargs):
        id = self.__builder.resourceId(*args, **kwargs)
        # try memcache
        if self.__memCache:
            if id in self.__cache:
                self.__log.info('mem-cache retrieve success: %s' % id)
                return self.__cache[id]
        # load from disk cache, or build resource
        cached = self.__cacheFolderLookup(id)
        if cached:
            self.__log.info('retrieve success: %s' % id)
            if self.__memCache: self.__cache[id] = cached
            return cached
        else:
            self.__log.info('retrieve fail, building: %s' % id)
            res = self.__builder(*args, **kwargs)
            self.__saveResource(res)
            if self.__memCache: self.__cache[id] = res
            return res

    def __cacheFolderLookup(self, id):
        '''
        :return: cached resource or None
        '''
        f = self.__folderById(id)
        if path.exists(f): return loadResource(f)
        else: return None

    def __saveResource(self, res):
        saveResource(res, self.__folderById(res.id))

    def __folderById(self, id):
        '''
        Given resource's id, return full path of the folder where
         resource is or will be stored.
        '''
        return path.join(self.__folder, str(id))

if __name__ == '__main__':
    FolderResourceCache(None, None)