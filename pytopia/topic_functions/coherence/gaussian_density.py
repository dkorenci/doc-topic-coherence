from pytopia.tools.IdComposer import IdComposer
from pytopia.resource.tools import tfIdfMatrix

from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA

class GaussCoherence(IdComposer):
    '''
    Calculates coherence as probability of the tf-idf vectors of
     top documetns with regard to fitted n-dimensional gaussian model.
    '''

    def __init__(self, dimReduce=None, covariance='diag',
                 score = 'll', seed=12345):
        '''
        :param dimReduce: if True,
        :param covariance: full, diag, spherical
        :param score: ll (log likelihood), aic, bic
        :param seed: random seed for initialization
        '''
        self.seed = seed
        self.covariance = covariance
        self.dimReduce = dimReduce
        self.score = score
        IdComposer.__init__(self)

    # requires corpus_topic_index_builder
    # requires corpus_tfidf_builder
    def __call__(self, topic):
        '''
        :param topic: (modelId, topicId)
        :return:
        '''
        m = tfIdfMatrix(topic, 100)
        if self.dimReduce == 'pca':
            #print m.dtype, m.shape
            m = PCA(n_components=5).fit_transform(m)
        gm = GaussianMixture(n_components=1, covariance_type=self.covariance,
                             n_init=1,
                             random_state=self.seed)
        gm.fit(m)
        if self.score == 'll': return gm.score(m)
        elif self.score == 'aic': return -gm.aic(m)
        elif self.score == 'bic': return -gm.bic(m)
