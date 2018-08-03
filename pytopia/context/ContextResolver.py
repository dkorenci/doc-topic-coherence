from pytopia.context.GlobalContext import GlobalContext

class ContextResolver(object):
    '''
    Helper for context resolution, classes requiring resolution
     define local (method-level, ...), object-level context ('context' property)
     and call ctx() to get context and resolve() to get objects within the context.
    '''

    def __init__(self, ctx=None):
        '''
        :param ctx: object-level context
        '''
        self.__ctx = ctx

    @property
    def context(self): return self.__ctx

    @context.setter
    def context(self, ctx_): self.__ctx = ctx_

    def ctx(self, local=None):
        '''
        Examine contexts for current object by priority,
        return first defined (non-empty) context.
        Priority of contexts is: local (ex. method-level), object-level, global
        '''
        if local: return local
        if hasattr(self, 'context'):
            if self.context: return self.context
        return GlobalContext.get()

    def resolve(self, *objects, **params):
        '''
        For each param, if it is of type describing an id (string, int, ...)
         use context to fetch the object by id, else just return object itself
        :param objects: list of objects representing ids
        :param params: only 'local' param is checked, to get local context
        :return:
        '''
        if len(objects) == 0: return None
        local = params['local'] if 'local' in params else None
        ctx = self.ctx(local)
        if len(objects) == 1: return resolveObject(objects[0], ctx)
        else: return tuple(resolveObject(o, ctx) for o in objects)

def resolve(*objects, **params):
    '''
    For each param, if it is of type describing an id (string, int, ...)
     use given (param 'context') or global to fetch the object by id,
     else just return object itself
    :param objects: list of objects representing ids
    :param params: only 'context' param is checked, to get local context
    :return:
    '''
    if len(objects) == 0: return None
    # get context
    ctx = params['context'] if 'context' in params else None
    if ctx is None: ctx = GlobalContext.get()
    # resolve objects
    if len(objects) == 1: return resolveObject(objects[0], ctx)
    else: return tuple(resolveObject(o, ctx) for o in objects)

def resolveObject(object, ctx):
    if isId(object):
        if object in ctx:
            return ctx[object]
        else:
            return None
    return object

def isId(object):
    '''
    True if object is of a type representing ids, such as int, string, ...
    :return:
    '''
    if isinstance(object, (int, long, str, unicode)): return True
    else: return False

def resolveIds(*objects):
    '''
    Each param should be either object with 'id' property or an
      object representing an id (int, string, ...)
    :param objects:
    :return: ids for the objects
    '''
    if len(objects) == 0: return None
    if len(objects) == 1: return resolveId(objects[0])
    else: return tuple(resolveId(o) for o in objects)

def resolveId(obj):
    '''
    :return: object if it is an id itself, else object.id
    '''
    if obj is None: return None
    if isId(obj): return obj
    elif hasattr(obj, 'id'): return obj.id
    else: raise Exception('object [%s] is neither an id nor an id-able'%obj)

if __name__ == '__main__':
    ContextResolver().resolve(1,2,3)
