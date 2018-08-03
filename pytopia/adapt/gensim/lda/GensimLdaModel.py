from pytopia.topic_model.TopicModel import TopicModel, Topic
from pytopia.adapt.gensim.lda.ldamodel_mod import LdaModel as LdaModel_mod
from pytopia.context.ContextResolver import resolve

from pytopia.tools.IdComposer import IdComposer
from pytopia.resource.loadSave import objectSaveFile

import pickle, os, numpy as np
from os.path import join

class GensimLdaModel(TopicModel, IdComposer):
    '''
    Pytopia adapter for gensim LdaModel
    '''
    
    def __init__(self, model, id = None, cacheTopics = True):
        '''
        :param model: gensim LdaModel or compatible
        :param label: additional data used for model identification
        :param cacheTopics: if True topic matrix of gensim model is copied
                and not calculated on every access
        '''
        IdComposer.__init__(self, ['corpus', 'dictionary', 'text2tokens',
                                   'options'])
        self.id = id
        if model is not None:
            if not isinstance(model, LdaModel_mod) :
                raise TypeError('model must be of type ldamodel')
            self.__init_gensim_data(model)
        self.cacheTopics = cacheTopics

    def numTopics(self):
        return self.model.num_topics

    def __initDataAfterLoad(self, model):
        # because of older models for which topicMatrix was not cleared
        if 'topicMatrix' in self.__dict__: del self.__dict__['topicMatrix']
        self.__init_gensim_data(model)

    def __init_gensim_data(self, model):
        'init model related data from LdaModel'
        self.model = model
        self.state = model.state
        self.num_topics = model.num_topics

    def __clearDataBeforeSave(self):
        '''Remove attributes that are not to be pickled.'''
        if 'topicMatrix' in self.__dict__: del self.__dict__['topicMatrix']
        self.__clear_gensim_data()

    def __clear_gensim_data(self):
        'delete all attributes holding LdaModel data'
        att2del = ['model', 'state', 'num_topics']
        for att in att2del: del self.__dict__[att]

    def topicIds(self):
        return range(self.num_topics)

    def topic(self, index):
        return Topic(self, index, self.topicVector(index))

    def topicVector(self, index):
        if hasattr(self, 'cacheTopics') and self.cacheTopics:
            if not hasattr(self, '_topicMatrix'):
                self.__copyTopicMatrix()
            return self._topicMatrix[index]
        else:
            topic = self.state.get_lambda()[index].copy()
            topic = topic / topic.sum()
            return topic

    def __copyTopicMatrix(self):
        '''
        Copy topic matrix from gensim model, and normalize
        '''
        self._topicMatrix = self.state.get_lambda().copy()
        for i in range(self._topicMatrix.shape[0]):
            row = self._topicMatrix[i]
            row /= row.sum()

    def inferTopics(self, txt, batch=False, format='tokens'):
        '''
        Calculate document-topic proportions for text(s).
        :param txt: text or iterable of texts
        :param batch: it True, txt is iterable of text, otherwise a single text
        :param format of a single text:
            'tokens' - list of tokens, 'bow' - list of (wordId, wordCount), 'string'
        :return: if a single text, single doc-topic vector, else a list of doc-topic vectors
        '''
        if batch: texts = [t for t in txt]
        else: texts = [txt]
        if format == 'tokens':
            dict_ = resolve(self.dictionary)
            texts = [dict_.tokens2bow(t) for t in texts]
        elif format == 'bow': pass # already in correct format
        else: raise Exception('format %s not supported' % format)
        result = self.model.inference(texts, collect_sstats=False)
        vectors = result[0] # first part of the result 2-tuple is a list of vectors
        for vec in vectors: vec /= vec.sum() # normalize to prob. distribution
        if batch: return vectors
        else: return vectors[0]

    __gensim_file = 'gensim_ldamodel'
    def save(self, folder):
        if not os.path.exists(folder): os.makedirs(folder)
        self.model.save(join(folder, GensimLdaModel.__gensim_file))
        model = self.model
        self.__clear_gensim_data()
        pickle.dump(self, open(join(folder, objectSaveFile), 'wb'))
        self.__init_gensim_data(model)

    def load(self, folder):
        gensim_model = LdaModel_mod.load(join(folder, GensimLdaModel.__gensim_file))
        self.__initDataAfterLoad(gensim_model)
        TopicModel.load(self, folder)

    def perplexity(self, docs):
        'return perplexity for bag of words represented documents'
        bound = self.model.log_perplexity(docs)
        pplexity = np.exp2(-bound)
        return pplexity

    def topicPriors(self):
        alphas = {}
        for i in range(self.model.num_topics): alphas[i] = self.model.alpha[i]
        return alphas