from pytopia.tools.IdComposer import IdComposer
from pytopia.context.ContextResolver import resolveIds, resolve

import numpy as np

class TopicDistVectorizer(IdComposer):
    '''
     Vectorizes texts by either concatenating topic distributions for the text
     from several predefined topic models, or using a models passed at
     vectorization time together with the text.
    '''

    def __init__(self, corpus, models=None):
        '''
        :param corpus:
        :param models: list of model Ids, or None
        '''
        self.corpus = resolveIds(corpus)
        self.models = '_'.join(str(m) for m in models) if models else None
        IdComposer.__init__(self)
        self.__modelTopicOrder = {}
        self.__models = models
        self.__ctiCache = {}

    def __call__(self, textId, model=None):
        '''
        :param textId:
        :param model: topic model id
        :return:
        '''
        if self.models: models = self.__models
        else: models = [model]
        vecs = []
        for modelId in models:
            cti = self.__getCorpusTopicIndex(modelId)
            topicVals = cti.textTopics(textId)
            model = resolve(modelId)
            vecs.append(self.__topics2vector(topicVals, model))
        return np.concatenate(vecs)

    # requires: corpus_topic_index_builder
    def __getCorpusTopicIndex(self, modelId):
        '''
        Build corpus topic index or retrieve from cache.
        '''
        if not modelId in self.__ctiCache:
            # todo there is already memcache at pytopia level,
            # the problem is logging the accesses that slows things down
            ctiBuilder = resolve('corpus_topic_index_builder')
            cti = ctiBuilder(corpus=self.corpus, model=modelId)
            self.__ctiCache[modelId] = cti
        return self.__ctiCache[modelId]

    def __topics2vector(self, topicVals, model):
        '''
        Convert values assigned to topics to numpy vector
        assuring the predictable order of topic positions.
        :param topicVals: map { topicId: topicTextValue}
        :param model: TopicModel-like
        :return:
        '''
        if model.id not in self.__modelTopicOrder:
            # create model's topic ordering
            ids = model.topicIds()
            mto = { tid : i for i, tid in enumerate(ids) }
            self.__modelTopicOrder[model.id] = mto
        mto = self.__modelTopicOrder[model.id]
        #assert len(mto) == len(topicVals)
        v = np.empty(len(mto), dtype=np.float64)
        for tid, tv in topicVals.iteritems():
            v[mto[tid]] = tv
        #assert np.abs(v.sum()-1.0) < 1e-5
        return v