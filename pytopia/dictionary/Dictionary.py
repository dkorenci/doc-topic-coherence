class Dictionary(object):
    '''
    Defines interface for Dictionary-like objects.
    Dictionary is a mapping between string tokens and integer indices.
    'id' attribute is mandatory.
    If dictionary adapts/wraps another dictionary object it should
     expose 'wrapped' property pointing to the object
    '''

    def maxIndex(self):
        '''Returns maximum index of words in the dictionary'''
        if not hasattr(self, '__maxIndex'):
            self.__maxIndex = -1
            for tok, ind in self.iteritems():
                if ind > self.__maxIndex: self.__maxIndex = ind
        return self.__maxIndex

    def token2index(self, token): pass

    def index2token(self, index):
        '''Return token for a given index'''
        if not hasattr(self, '__ind2tok'):
            self.__ind2tok = { ind:tok for tok, ind in self.iteritems() }
        return self.__ind2tok[index]

    def __getitem__(self, token): return self.token2index(token)

    def __contains__(self, item): pass

    def __len__(self): pass

    def __iter__(self):
        '''Iterate over tokens in the dictionary'''
        return self.iterkeys()

    def tokens2bow(self, tokens):
        '''
        :param tokens: list-like of string tokens
        :return: list of (tokenIndex, tokenCount) pairs, one for each distinct token
        '''
        from copy import copy
        cnt = {}
        for tok in tokens:
            ind = self.token2index(tok)
            if ind in cnt: cnt[ind] += 1
            else: cnt[ind] = 1
        res = copy(cnt.items())
        res.sort(key=lambda indCnt: indCnt[0]) # sort by token indices
        return res

    def iteritems(self): pass
    def items(self): return [i for i in self.iteritems()]

    def iterkeys(self): pass
    def keys(self): return [k for k in self.iterkeys()]

    def itervalues(self):pass
    def values(self): return [v for v in self.itervalues()]

    def __eq__(self, other):
        '''
        Dicts are considered equal if they contain the same tokens
         and matching tokens have same indices.
        '''
        if self.maxIndex() != other.maxIndex(): return False
        return indexedTokensList(self) == indexedTokensList(other)

def indexedTokensList(dict_):
    '''
    Create list of (token, index) pairs for all the dictionary tokens
        and sort it by index. For dictionary comparison.
    :param dict_: pytopia Dictionary
    '''
    toki = [(tok, dict_[tok]) for tok in dict_]
    toki.sort(key=lambda ti: ti[1])
    return toki