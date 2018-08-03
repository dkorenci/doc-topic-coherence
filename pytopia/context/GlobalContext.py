from pytopia.context.StackedContext import StackedContext

class GlobalContext():
    '''
    Class representing application-level pytopia context
    '''
    @classmethod
    def set(cls, ctx):
        GlobalContext._ctx = StackedContext(None, ctx)

    @classmethod
    def get(cls):
        GlobalContext._init()
        return GlobalContext._ctx

    @classmethod
    def _init(cls):
        '''
        If global context does not already exist, init as empty stacked context.
        '''
        if not hasattr(cls, '_ctx'):
            GlobalContext._ctx = StackedContext('global_context')

    @classmethod
    def push(cls, ctx):
        GlobalContext._init()
        GlobalContext._ctx.push(ctx)

    @classmethod
    def pop(cls):
        GlobalContext._init()
        GlobalContext._ctx.pop()

def printGlobal(): print GlobalContext.get()