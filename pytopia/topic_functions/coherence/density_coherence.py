from pytopia.tools.IdComposer import IdComposer

from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA

from numpy import median

class GaussCoherence(IdComposer):
    '''
    Calculates matrix coherence as probability row vectors
     given by fitted n-dimensional gaussian model.
    '''

    def __init__(self, dimReduce=None, covariance='diag',
                 center='mean', seed=12345):
        '''
        :param dimReduce: None or number of components to reduce to with PCA
        :param covariance: full, diag, spherical
        :param scoreMeasure: ll (log likelihood), aic, bic
        :param seed: random seed for initialization
        '''
        self.covariance = covariance
        self.dimReduce = dimReduce
        self.center = center
        IdComposer.__init__(self)
        self.seed = seed

    def __call__(self, m):
        '''
        :param m: matrix
        :return:
        '''
        if self.dimReduce is not None:
            m = PCA(n_components=self.dimReduce).fit_transform(m)
        gm = GaussianMixture(n_components=1, covariance_type=self.covariance,
                             n_init=1, random_state=self.seed)
        gm.fit(m)
        ss = gm.score_samples(m)
        if self.center == 'mean': return ss.mean()
        elif self.center == 'median': return median(ss)
        else: raise Exception('unkown measure of center: %s' % str(self.center))