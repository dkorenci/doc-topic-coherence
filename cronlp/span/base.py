'''
Basic classes for working with spans.
'''

class Span:
    def __init__(self, start, end, text, type):
        self.start, self.end = start, end
        self.text, self.type = text, type

    def __str__(self): return self.covered()

    def details(self):
        return '[%s] type:%s start:%d end:%d' % \
               (self.covered(), self.type, self.start, self.end)

    def covered(self, normalizeWs = True):
        'text covered by span'
        text = self.text[self.start:self.end]
        if normalizeWs: text = ' '.join(text.split())
        return text

    def lcovered(self, normalizeWs = True):
        'lowercased text covered by span'
        return self.covered(normalizeWs).lower()

    def __contains__(self, item):
        if isinstance(item, 'Span'):
            return item.start >= self.start and item.end <= self.end
        else: return False