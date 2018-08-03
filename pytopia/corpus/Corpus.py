class Corpus(object):
    '''
    Defines interface of Corpus-like objects.
    Corpus represents a collection of Text-like (texts) objects and
     provides methods for fetching texts and iterating over texts.
     'id' is a madatory attribute/property.
    Each text in a corpus is expected to have a unique id.
    '''

    def getText(self, id):
        '''Fetch single text by id using getTexts method,
        so a subclass of Corpus only needs to implement getTexts. '''
        result = [ txt for txt in self.getTexts([id]) ]
        if len(result) == 0 : return None
        else : return result[0]

    def getTexts(self, ids):
        '''Fetch collection of texts by list of ids. '''

    def __iter__(self):
        '''Iterate over texts in the corpus. '''

    def textIds(self):
        '''get ids of all the texts in the corpus'''
        return [ txto.id for txto in self ]

    def __len__(self):
        if not hasattr(self, 'length'):
            # cache the corpus length
            self.__length = sum(1 for _ in self)
        return self.__length
