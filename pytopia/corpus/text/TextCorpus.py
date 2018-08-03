from pytopia.corpus.Corpus import Corpus
from pytopia.corpus.text.parse import parseLine

from copy import copy

class TextCorpus(Corpus):
    '''
    Simple corpus for testing, built from string, with one Text per line.
    '''

    def __init__(self, text, id=None):
        self.id = id
        self.__txt = text
        self.__parseText()

    def __parseText(self):
        '''Parse text and create corpus'''
        self.texts = [parseLine(l) for l in self.__txt.splitlines() if l.strip()]

    def getTexts(self, ids):
        '''Fetch collection of texts by list of ids. '''
        return copy(self.texts)

    def __iter__(self):
        '''Iterate over texts in the corpus. '''
        return iter(self.texts)

