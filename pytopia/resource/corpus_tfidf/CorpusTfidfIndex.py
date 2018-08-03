from pytopia.context.ContextResolver import resolveIds, resolve
from pytopia.tools.IdComposer import IdComposer
from pytopia.resource.loadSave import pickleObject
from pytopia.tools.logging import resbuild_logger

from sklearn.feature_extraction.text import TfidfTransformer
from scipy.sparse import dok_matrix, save_npz, load_npz, find, isspmatrix

import numpy as np

from os import path

@resbuild_logger
class CorpusTfidfBuilder():

    def __init__(self, sparse=False):
        self.__sparse = sparse

    def __call__(self, corpus, dictionary, text2tokens):
        ctfidf = CorpusTfidfIndex(corpus, dictionary, text2tokens)
        ctfidf.build(self.__sparse)
        return ctfidf

    def resourceId(self, corpus, dictionary, text2tokens):
        return CorpusTfidfIndex(corpus, dictionary, text2tokens).id


class CorpusTfidfIndex(IdComposer):
    '''
    Creates, stores and enables access to tfidf vectors for a pytopia corpus.
    '''

    def __init__(self, corpus, dictionary, text2tokens):
        self.corpus, self.dictionary, self.text2tokens = \
            resolveIds(corpus, dictionary, text2tokens)
        IdComposer.__init__(self, ['corpus', 'dictionary', 'text2tokens'])

    def __call__(self, textId, format='ndarray'):
        return self.tfidf(textId, format)

    def tfidf(self, textId, format='ndarray'):
        ''' Return tfidf vector for a text with given id. '''
        txtInd = self.corpus_index.id2index(textId)
        vec = self.__tfidf[txtInd]
        if format == 'sparse': return vec
        elif format == 'ndarray':
            r = np.zeros(vec.shape[1])
            ri, ci, v = find(vec)
            for i in xrange(len(v)): r[ci] = v
            return r
        else: raise Exception('invalid format: %s' % format)

    def __getitem__(self, textId): return self.tfidf(textId)

    def __len__(self):
        return self.__tfidf.shape[0]

    def __iter__(self):
        for i in range(self.__tfidf.shape[0]):
            yield self.__tfidf[i]

    def __eq__(self, other):
        if not isinstance(other, self.__class__): return False
        if self.id != other.id: return False
        if len(self) != len(other): return False
        if not self.corpus_index == other.corpus_index: return False
        for txtId in self.corpus_index:
            vec1, vec2 = self.tfidf(txtId), other.tfidf(txtId)
            if isinstance(vec1, np.ndarray) and isinstance(vec2, np.ndarray):
                if not np.array_equal(vec1, vec2): return False
            elif isspmatrix(vec1, np.ndarray) and isspmatrix(vec2, np.ndarray):
                if (self.tfidf(txtId) != other.tfidf(txtId)).nnz != 0 : return False
            else:
                # todo implement comparison of ndarrays and sparse matrices
                raise NotImplementedError()
        return True

    @property
    def corpus_index(self):
        if not hasattr(self, '_cindex'):
            cindBuild = resolve('corpus_index_builder')
            self._cindex = cindBuild(self.corpus)
        return self._cindex

    # requires: bow_corpus_builder
    def build(self, sparse=False):
        '''
        :param sparse: if True, use sparse matrix for doc-wordCount matrix,
            which saves memory but is much slower.
        :return:
        '''
        bowBuilder = resolve('bow_corpus_builder')
        bowCorpus = bowBuilder(corpus=self.corpus, text2tokens=self.text2tokens,
                               dictionary=self.dictionary)
        dict = resolve(self.dictionary)
        # TODO use bowCorpus.corpusMatrix() instead of manually building
        rows, cols = len(bowCorpus), dict.maxIndex()+1
        if sparse: counts = dok_matrix((rows, cols), dtype=np.uint32)
        else: counts = np.zeros((rows, cols), dtype=np.uint32)
        for i, bow in enumerate(bowCorpus):
           counts[i] = bow2Vector(bow, cols, sparse=sparse)
        tfidf = TfidfTransformer(sublinear_tf=True)
        self.__tfidf = tfidf.fit_transform(counts)

    def corpusMatrix(self):
        # TODO solve framework-wide data passing: refs or copies
        return self.__tfidf

    def save(self, folder):
        if hasattr(self, '_cindex'): delattr(self, '_cindex')
        pickleObject(self, folder)
        save_npz(self.__tfidfMatrixFname(folder), self.__tfidf)

    def load(self, folder):
        self.__tfidf = load_npz(self.__tfidfMatrixFname(folder))

    def __tfidfMatrixFname(self, f):
        return path.join(f, 'tfidfMatrix.npz')


def bow2Vector(bow, vectorSize, type=np.uint32, sparse=False):
    '''
    Transform bow, list-like of (index, count) to scipy sparse vector.
    :param type: dtype large enough to hold counts
    '''
    if sparse:
        v = dok_matrix((1, vectorSize), dtype=type)
        for i, cnt in bow: v[0, i] = cnt
    else:
        v = np.zeros(vectorSize, dtype=type)
        for i, cnt in bow: v[i] = cnt
    return v
