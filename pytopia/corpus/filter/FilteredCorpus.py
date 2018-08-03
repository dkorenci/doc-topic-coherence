# corpus classes that filter other, wrapped corpora

from pytopia.corpus.Corpus import Corpus

class FilteredCorpus(Corpus):
    '''
    Corpus filtering texts of another corpus by a specified criteria.
    '''

    def __init__(self, id, corpus, filter):
        '''
        :param corpus: base corpus
        :param filter: single callable accepting Text object and
            returning True/False (filtered/not filtered), or list of such objects.
            If a list is given, text is filtered if any filter rejects it.
        '''
        self.corpus = corpus; self.id = id
        if isinstance(filter, list): self.filters = filter
        else: self.filters = [ filter ]

    def __filtered(self, textobj):
        for f in self.filters:
            if f(textobj): return True
        return False

    def __iter__(self):
        for txto in self.corpus:
            if not self.__filtered(txto): yield txto

    def getTexts(self, ids):
        'get texts that pass the filter '
        texts = self.corpus.getTexts(ids)
        return [txto for txto in texts if not self.__filtered(txto)]

    def getText(self, id):
        'get text if it passes filter, None otherwise'
        txto = self.corpus.getText(id)
        if txto is None : return None
        if self.__filtered(txto) : return None
        else: return txto

    def textIds(self):
        return [ txto.id for txto in self.corpus if not self.__filtered(txto) ]