from pytopia.context.ContextResolver import resolve, resolveIds
from pytopia.tools.IdComposer import IdComposer
from pytopia.resource.loadSave import pickleObject
from pytopia.resource.ResourceBuilder import SelfbuildResourceBuilder

import numpy as np
from scipy.sparse import spmatrix, save_npz, load_npz
from scipy.sparse import csr_matrix as sparse_type
from os import path
from time import time

class CorpusTextVectors(IdComposer):
    '''
    Based on a component that vectorizes corpus texts,
    this is a static store of vectors of corpus text.
    '''

    def __init__(self, vectorizer, corpus=None, verbose=False):
        '''
        :param vectorizer: callable accepting text objects or text ids and
         returning vectors of the same type (ndarray or scipy sparse), shape and stored scalar type.
        :param corpus: if None and if vectorizer has a 'corpus' property it is used as corpus
        '''
        self.vectorizer = vectorizer
        if corpus is None:
            if hasattr(vectorizer, 'corpus'): self.corpus = resolveIds(vectorizer.corpus)
            else: raise Exception('corpus must be specified')
        else: self.corpus = resolveIds(corpus)
        IdComposer.__init__(self, attributes=['vectorizer'])
        self.verbose = verbose

    def __len__(self): return self._m.shape[0]

    def __call__(self, text):
        txtid = resolveIds(text)
        return self._m[self.corpus_index.id2index(txtid)]

    def __eq__(self, other):
        if self.sparse != other.sparse: return False
        if self._m.dtype != other._m.dtype: return False
        if self._m.shape != other._m.shape: return False
        if self.sparse: return (self._m - other._m).nnz == 0
        else: return (self._m == other._m).all()

    @property
    # requires corpus_index_builder
    def corpus_index(self):
        if not hasattr(self, '_cindex'):
            cindBuild = resolve('corpus_index_builder')
            self._cindex = cindBuild(self.corpus)
        return self._cindex

    # requires corpus_index_builder
    def build(self):
        ci = self.corpus_index
        corpus = resolve(self.corpus)
        self._m = None # matrix for storing coprus vector
        rows = len(ci)
        for txto in corpus:
            if self.verbose: print txto.id
            t0 = time()
            vec = self.vectorizer(txto)
            if self.verbose: print ' time 2 vectorize %.4f' % (time()-t0)
            if self._m is None: # init matrix
                if isinstance(vec, np.ndarray):
                    cols = vec.shape[0]
                    self._m = np.empty(shape=(rows, cols), dtype=vec.dtype)
                    self.sparse = False
                elif isinstance(vec, spmatrix):
                    cols = vec.shape[1]
                    self._m = sparse_type((rows, cols), dtype=vec.dtype)
                    self.sparse = True
                else: raise Exception('Unsuported vector type: %s' % str(type(vec)))
            t0 = time()
            # if self.sparse and not(isinstance(vec, sparse_type)):
            #     vec = sparse_type(vec)
            #print vec.shape, type(vec)
            #print self._m.shape, type(self._m)
            r = ci.id2index(txto.id)
            self._m[r] = vec
            if self.verbose: print ' time 2 write 2 matrix %.4f' % (time() - t0)

    def save(self, folder):
        pickleObject(self, folder)
        if self.sparse: save_npz(self.__sparseMatrixFname(folder), self._m)
        else: np.save(self.__ndarrayFname(folder), self._m)

    def load(self, folder):
        if self.sparse: self._m = load_npz(self.__sparseMatrixFname(folder))
        else: self._m = np.load(self.__ndarrayFname(folder))

    def __sparseMatrixFname(self, f): return path.join(f, 'corpusMatrix.npz')
    def __ndarrayFname(self, f): return path.join(f, 'corpusMatrix.npy')

    def __getstate__(self):
        return self.sparse, self.corpus, IdComposer.__getstate__(self)

    def __setstate__(self, state):
        self.sparse, self.corpus, idcState = state
        IdComposer.__setstate__(self, idcState)

CorpusTextVectorsBuilder = SelfbuildResourceBuilder(CorpusTextVectors)