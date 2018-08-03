from pytopia.tools.IdComposer import IdComposer
from pytopia.topic_functions.tools import smallToZero

import numpy as np
from scipy.sparse import spmatrix

class VarianceCoherence(IdComposer):
    '''
    Calculates coherence as inverse of the 'variance', where variance
     is average distance between vectors and their mean.
    '''

    def __init__(self, distance, center='mean', exp=1.0):
        self.distance = distance
        self.center = center
        if center == 'mean':
            self.exp = exp
            IdComposer.__init__(self)
        elif center == 'median':
            # raising to positive power does not influence median
            IdComposer.__init__(self)
        else: raise Exception('Invalid measure of center %s' % center)

    def __call__(self, m):
        if isinstance(m, np.ndarray): return self.__ndVariance(m)
        elif isinstance(m, spmatrix): return self.__sparseVariance(m)
        else: raise Exception('unsuported matrix type')

    def __ndVariance(self, m):
        a = np.average(m, axis=0)
        ad = np.array([self.distance(r, a) for r in m])
        smallToZero(ad)
        if self.center == 'mean' and self.exp != 1.0:
            ad = np.power(ad, self.exp)
        if self.center == 'mean': c = np.average(ad)
        else: c = np.median(ad)
        return -c

    def __sparseVariance(self, m):
        from sys import getsizeof as size
        from scipy.sparse import coo_matrix, dok_matrix
        from time import time
        t0 = time()
        N = m.shape[0]  # num. rows
        a = dok_matrix(m.mean(axis=0))
        print 'average non zero', a.nnz
        #diff = m - a
        # m = coo_matrix(diff)
        for r in xrange(m.shape[0]):
            m[r, :] = m[r, :] - a
        m = coo_matrix(m)
        m = m.multiply(m)
        v = m.sum() / N
        print 'variance time %.4f' % (time()-t0)
        return -v

def sparseSumSquares(m):
    r, c = m.nonzero()
    res = 0.0
    print 'nonzero', m.nnz
    for i in xrange(len(r)):
        e = m[r[i], c[i]]
        res += e*e
    return res