'''
Methods that calculate some measure of coherence of a set of vectors
given as rows of a matrix. Vectors represent related documents.
'''

import numpy as np

from pytopia.tools.IdComposer import IdComposer
from pytopia.topic_functions.tools import smallToZero

class AverageVectorDistCoh(IdComposer):
    '''
    Calculates coherence of a set of vectors (given as matrix rows)
    as average distance between pairs of vectors.
    '''

    def __init__(self, distance, center='mean', exp=1.0):
        '''
        :param distance: distance function
        :param exp: each distance is raised to power exp > 0
        :param center: 'mean' or 'median'
        '''
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
        N = m.shape[0]  # num. rows
        dm = self.distance(m, m) # must return N x N matrix of row distances
        da = dm[np.triu_indices(N, 1)] # distance array: upper triangle, flattened
        smallToZero(da)
        if self.center == 'mean' and self.exp != 1.0:
            da = np.power(da, self.exp)
        if self.center == 'mean': c = np.average(da)
        else: c = np.median(da)
        return -c


