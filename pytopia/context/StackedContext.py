from pytopia.context.Context import BaseContext

class StackedContext(BaseContext):

    def __init__(self, id, context=None):
        BaseContext.__init__(self, id)
        self._stack = []
        if context is not None: self.push(context)

    def push(self, ctx): self._stack.append(ctx)

    def pop(self):
        if self._stack: return self._stack.pop()

    def __getitem__(self, id):
        for ctx in self._stack[::-1]:
            res = ctx[id]
            if res is not None: return res
        return None

    def __contains__(self, id):
        for ctx in self._stack[::-1]:
            if id in ctx: return True
        return False

    def __str__(self):
        s = '%s_id[%s]' % (self.__class__.__name__, self.id)
        if not self._stack: s += ' empty'
        else:
            s += '\n'
            for l in range(len(self._stack))[::-1]:
                s += '*** LEVEL %d CONTEXT:\n%s' % (l, str(self._stack[l]))
        return s
