from pytopia.dictionary.Dictionary import Dictionary
from pytopia.resource.loadSave import pickleObject
from pytopia.tools.IdComposer import IdComposer
from pytopia.context.ContextResolver import resolveIds


class BasicDictionary(Dictionary, IdComposer):
    '''
    Basic python implementation of Dictionary interface,
    using two dictionaries to map tokens to indices and vice versa.
    '''

    def __init__(self, corpus=None, text2tokens=None, label=None):
        self._tok2ind = dict()
        self._ind2tok = dict()
        self._maxind = None
        corpus, text2tokens = resolveIds(corpus, text2tokens)
        if corpus is not None: self.corpus = corpus
        if text2tokens is not None: self.text2tokens = text2tokens
        if label is not None: self.label = label
        IdComposer.__init__(self)

    def addToken(self, tok):
        '''
        Add single string-like token to dictionary
        '''
        if tok in self._tok2ind: return
        if self._maxind is None: self._maxind = 0
        else: self._maxind += 1
        self._tok2ind[tok] = self._maxind
        self._ind2tok[self._maxind] = tok

    def addTokens(self, tokens):
        '''
        Add iterable of tokens to dictionary.
        '''
        for tok in tokens: self.addToken(tok)

    def __len__(self): return self._maxind + 1 if self._maxind is not None else 0

    def maxIndex(self): return self._maxind

    def token2index(self, token): return self._tok2ind[token]

    def index2token(self, index): return self._ind2tok[index]

    def __getitem__(self, token): return self._tok2ind[token]

    def __contains__(self, token): return token in self._tok2ind

    def __iter__(self): return self.iterkeys()

    def iteritems(self): return self._tok2ind.iteritems()

    def iterkeys(self): return self._tok2ind.iterkeys()

    def itervalues(self): return self._ind2tok.iterkeys()

    def save(self, folder):
        pickleObject(self, folder)

    def __getstate__(self):
        return self._tok2ind, self._ind2tok, self._maxind, \
                IdComposer.__getstate__(self),

    def __setstate__(self, state):
        self._tok2ind, self._ind2tok, self._maxind, idcState = state
        IdComposer.__setstate__(self, idcState)
