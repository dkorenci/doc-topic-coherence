from pytopia.context.ContextResolver import ContextResolver, resolve, resolveIds
from pytopia.tools.IdComposer import IdComposer
from pytopia.resource.loadSave import pickleObject

from pytopia.tools.logging import resbuild_logger

from scipy.sparse import dok_matrix

@resbuild_logger
class BowCorpusBuilder():
    '''
    Creates corpus of bag-of-words documents for a pytopia-corpus.
    Such document is iterable of (wordIndex, wordCount) pairs.
    '''

    def __init__(self, ctx=None):
        '''
        :param ctx: pytopia context
        '''
        self.__ctx = ctx

    def __call__(self, corpus, text2tokens, dictionary):
        bowc = BowCorpus(corpus, text2tokens, dictionary, self.__ctx)
        bowc.build()
        return bowc

    def resourceId(self, corpus, text2tokens, dictionary):
        return BowCorpus(corpus, text2tokens, dictionary, self.__ctx).id


import numpy as np
from os import path

class BowCorpus(IdComposer):
    '''
    Static corpus of bag-of-words documents, stores docs with 2d numpy array.
    Order of the documents is the same as in CorpusIndex for the corpus.
    Not a proper pytopia corpus.
    '''

    def __init__(self, corpus, txt2tok, dict, context=None, initSize=100):
        self.__cr = ContextResolver(context)
        corpus, txt2tok, dict = self.__cr.resolve(corpus, txt2tok, dict)
        self.corpus, self.txt2tok, self.dict = \
            resolveIds(corpus, txt2tok, dict)
        IdComposer.__init__(self, attributes=['corpus', 'txt2tok', 'dict'])
        self.__corpus = np.empty(initSize, dtype=np.object)
        self.__nd = 0 # number of documents
        self.__index = None

    # document access interace
    def __len__(self): return self.__nd
    def __getitem__(self, index): return self.__corpus[index]
    def __iter__(self):
        for i in range(self.__nd): yield self.__corpus[i]

    # todo method for fetching text sizes

    # requires: corpus_index_builder
    @property
    def corpus_index(self):
        if self.__index is None:
            cib = resolve('corpus_index_builder')
            self.__index = cib(self.corpus)
        return self.__index

    # pytopia resource interface
    def build(self):
        '''Perform build with constructor parameters. '''
        corpus, txt2tok, dict = self.__cr.resolve(self.corpus, self.txt2tok, self.dict)
        self.__nd = len(self.corpus_index)
        self.__corpus = np.resize(self.__corpus, self.__nd)
        for txto in corpus:
            bow = dict.tokens2bow(txt2tok(txto.text))
            self.__corpus[self.corpus_index.id2index(txto.id)] = bow
        self.__truncate()

    #todo: use corpus.tools.bowCorpus2Matrix
    def corpusMatrix(self, sparse=True, dtype=np.uint32):
        '''
        Create matrix from bow corpus.
        Rows are indices of documents, columns are dictionary indices of words words,
        values are number of words in the document.
        :param sparse: weather to return scipy.sparse matrix of np.ndarray
        '''
        from pytopia.corpus.tools import bow2Vector
        self.dict = resolve(self.dict)
        rows, cols = len(self), self.dict.maxIndex()+1
        if sparse: matrix = dok_matrix((rows, cols), dtype=dtype)
        else: matrix = np.zeros((rows, cols), dtype=dtype)
        for i, bow in enumerate(self):
           matrix[i] = bow2Vector(bow, cols, sparse=sparse)
        return matrix

    def save(self, folder):
        pickleObject(self, folder)
        np.save(self.__bowFileName(folder), self.__corpus)

    def load(self, folder):
        self.__corpus = np.load(self.__bowFileName(folder))
        self.__nd = len(self.__corpus)

    def __bowFileName(self, f):
        return path.join(f, 'bowCorpus.npy')

    def __addDocument(self, doc):
        '''
        Adds document to the end of corpus, resizing if necessary.
        :param doc: list-like of (wordIndex, wordCount)
        '''
        if self.__nd + 1 > len(self.__corpus):
            self.__corpus = np.resize(self.__corpus, len(self.__corpus) * 2)
        self.__corpus[self.__nd] = self.__docToArray(doc)
        self.__nd += 1

    def __truncate(self):
        '''Resize internal array to match number of documents. '''
        self.__corpus = np.resize(self.__corpus, self.__nd)

    def __docToArray(self, doc):
        array = np.empty(len(doc), dtype='u4,u4')
        for i in range(len(doc)): array[i] = doc[i]
        return array
