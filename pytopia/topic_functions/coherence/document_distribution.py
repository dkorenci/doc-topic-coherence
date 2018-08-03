import numpy as np

from pytopia.context.ContextResolver import resolve
from pytopia.tools.IdComposer import IdComposer
from pytopia.topic_functions.tools import cached_function


@cached_function
class DocuDistCoherence(IdComposer):
    '''
    Calculates coherence distance between two distributions over documents:
    distribution where probabilities are proportional to doc-topic proportions
    and uniform distribution.
    '''

    def __init__(self, measure):
        '''
        :param measure: measure of distance between two distributions
        '''
        self.measure = measure
        IdComposer.__init__(self)

    # requires corpus_topic_index_builder
    def __call__(self, topic):
        '''
        :param topic: (modelId, topicId)
        :return:
        '''
        mid, tid = topic
        model = resolve(mid)
        ctiBuilder = resolve('corpus_topic_index_builder')
        cti = ctiBuilder(corpus=model.corpus, model=model)
        topicTexts = cti.topicTexts(tid, sorted=None)
        # take document weights and normalize
        tdist = topicTexts[:, 1].astype(np.float64)
        tdist /= tdist.sum()
        numDocs = topicTexts.shape[0]
        tvac = np.repeat(1.0/numDocs, numDocs)
        return self.measure(tdist, tvac)
