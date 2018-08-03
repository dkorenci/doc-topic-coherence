from logging_utils.setup import *
from logging_utils.tools import fullClassName

class ResourceBuilderLogger():

    def __init__(self, builder):
        self.__builder = builder
        self.__log = createLogger(fullClassName(builder), INFO)

    def __call__(self, *args, **kwargs):
        id_ = self.__builder.resourceId(*args, **kwargs)
        self.__log.info('building resource: %s' % id_)
        return self.__builder(*args, **kwargs)

    def resourceId(self, *args, **kwargs):
        return self.__builder.resourceId(*args, **kwargs)

    @property
    def id(self):
        if hasattr(self.__builder, 'id'): return getattr(self.__builder.id)
        else: return None

def resbuild_logger(cls):
    def createObject(*args, **kwargs):
        return ResourceBuilderLogger(cls(*args, **kwargs))
    return createObject

