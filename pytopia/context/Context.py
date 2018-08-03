class BaseContext():

    def __init__(self, id):
        self.__id = id

    @property
    def id(self): return self.__id

    def __enter__(self):
        from pytopia.context.GlobalContext import GlobalContext
        GlobalContext.push(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        from pytopia.context.GlobalContext import GlobalContext
        GlobalContext.pop()
        if exc_type or exc_val or exc_tb: # exception raised in with block
            return False # signal to reraise exception

    def __getitem__(self, id): raise NotImplementedError

    def __contains__(self, id): raise NotImplementedError

    def __str__(self): raise NotImplementedError

class Context(dict, BaseContext):
    '''
    Implementation of a context for easy building from other contexts and id-able objects.
    Named Contex not to break compatibility with older code.
    todo: rename to SimpleContext or similar, rename BaseContext to Context
    '''

    def __init__(self, id, *objs):
        BaseContext.__init__(self, id)
        for o in objs: self.add(o)

    def merge(self, ctx):
        '''Add data from another context, overwriting existing ids'''
        self.update(ctx.iteritems())
        return self

    def add(self, idable):
        '''Add object with 'id' property'''
        self[idable.id] = idable

    def __str__(self):
        r = u'%s[id=%s]\n' % ('Context', self.id)
        for id, obj in self.iteritems():
            r += u'%s = %s\n' % (id, obj)
        return r

    def __getitem__(self, id):
        if id in self: return dict.__getitem__(self, id)
        else: return None

if __name__ == '__main__':
    ctx = Context('my_context')
    ctx['id']=2
    print ctx['id']
