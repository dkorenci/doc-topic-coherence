import numpy as np

class CachedFunction():
    '''
    Caches results of the underlying function to save time.
    '''

    def __init__(self, function):
        self.__f = function
        self.__cache = {}

    def __call__(self, arg):
        if arg not in self.__cache:
            self.__cache[arg] = self.__f(arg)
        return self.__cache[arg]

    @property
    def id(self):
        if hasattr(self.__f, 'id'): return self.__f.id
        else: return None

def cached_function(cls):
    def createObject(*args, **kwargs):
        return CachedFunction(cls(*args, **kwargs))
    return createObject

def smallToZero(m, eps=1e-10):
    '''
    Set very small values of ndarray to 0.
    Modifies m in place.
    :param m: ndarray
    :param eps: threshold for smallness
    '''
    m[np.abs(m) < eps] = 0.0
