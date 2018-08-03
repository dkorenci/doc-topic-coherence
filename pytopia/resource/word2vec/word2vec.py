from pytopia.tools.IdComposer import IdComposer
from pytopia.resource.loadSave import pickleObject
from pytopia.resource.ResourceBuilder import SelfbuildResourceBuilder

import numpy as np
from os import path

class Word2Vec(IdComposer):
    '''
    Resource for quickly loading word2vec vectors, stores them
    as word2index map and a ndarray of vectors.
    Created from original google format.
    '''

    def __init__(self, fname):
        '''
        :param fname: file with vectors stored in original google format,
                        with optional .bin extension
        :return:
        '''
        self.file = self.__idFromFname(fname)
        IdComposer.__init__(self)
        self.__fname = fname

    def __idFromFname(self, fname):
        id = path.basename(fname)
        if id.endswith('.bin'): id = id[:-4]
        return id

    def __len__(self): return self.__vectors.shape[0]

    def __call__(self, word):
        if word not in self.word2index: return None
        return self.__vectors[self.word2index[word]]

    def closest(self, word, numW=50):
        from scipy.spatial.distance import cdist
        if not hasattr(self, '_i2w'):
            self._i2w = { i:w for w, i in self.word2index.iteritems() }
        vec = self(word)
        vm = np.array([vec])
        from time import time
        t0 = time()
        dist = cdist(self.__vectors, vm, 'cosine')
        print time()-t0
        t0 = time()
        results = [ self._i2w[r[0]] for r in np.argsort(dist, axis=0)[:numW] ]
        print time() - t0
        return results

    def build(self):
        w2vMap = load_bin_vec(self.__fname)
        words = w2vMap.keys()
        rows = len(words)
        vec = w2vMap[words[0]]
        cols = vec.shape[0]
        self.word2index = {}
        self.__vectors = np.empty((rows, cols), dtype=np.float32)
        for i, wv in enumerate(w2vMap.iteritems()):
            w, vec = wv
            self.word2index[w] = i
            self.__vectors[i] = vec
        w2vMap = None
        import gc; gc.collect()

    def save(self, folder):
        pickleObject(self, folder)
        np.save(self.__VectorsNdarrayFname(folder), self.__vectors)
        np.save(self.__WordsNdarrayFname(folder), self.__wordIndex2ndarray())

    def __wordIndex2ndarray(self):
        a = np.empty(shape=len(self.word2index), dtype=np.object)
        for w, i in self.word2index.iteritems():
            a[i] = w
        return a

    def __wordIndexFromNdarray(self, a):
        return {w:i for i, w in enumerate(a)}

    def load(self, folder):
        self.__vectors = np.load(self.__VectorsNdarrayFname(folder))
        self.word2index = self.__wordIndexFromNdarray(
                                np.load(self.__WordsNdarrayFname(folder)) )

    def __VectorsNdarrayFname(self, f): return path.join(f, 'wordVectors.npy')

    def __WordsNdarrayFname(self, f): return path.join(f, 'words.npy')

    def __getstate__(self):
        return IdComposer.__getstate__(self)

    def __setstate__(self, state):
        idcState = state
        IdComposer.__setstate__(self, idcState)

Word2VecBuilder = SelfbuildResourceBuilder(Word2Vec)

def load_bin_vec(fname):
    """
    Code from: https://groups.google.com/forum/#!topic/word2vec-toolkit/GFNZkoDPd0g
    Loads 300x1 word vecs from Google (Mikolov) word2vec
    """
    word_vecs = {}
    with open(fname, "rb") as f:
        header = f.readline()
        vocab_size, layer1_size = map(int, header.split())
        binary_len = np.dtype('float32').itemsize * layer1_size
        for line in xrange(vocab_size):
            word = []
            while True:
                ch = f.read(1)
                if ch == ' ':
                    word = ''.join(word)
                    break
                if ch != '\n':
                    word.append(ch)
            word_vecs[word] = np.fromstring(f.read(binary_len), dtype='float32')
    return word_vecs

if __name__ == '__main__':
    load_bin_vec('/datafast/word2vec/GoogleNews-vectors-negative300.bin')