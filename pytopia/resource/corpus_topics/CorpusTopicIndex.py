from pytopia.tools.logging import resbuild_logger
from pytopia.tools.IdComposer import IdComposer
from pytopia.context.ContextResolver import resolve, isId, resolveIds, resolveId
from pytopia.resource.loadSave import pickleObject

from logging_utils.tools import fullClassName
from logging_utils.setup import *

import numpy as np
from os import path

@resbuild_logger
class CorpusTopicIndexBuilder():

    def __init__(self, ctx=None):
        '''
        :param ctx: pytopia context
        '''
        self.__ctx = ctx

    def __call__(self, corpus, model, dictionary=None, txt2tokens=None):
        ctindex = CorpusTopicIndex(corpus, model, dictionary, txt2tokens)
        ctindex.build()
        return ctindex

    def resourceId(self, corpus, model, dictionary=None, txt2tokens=None):
        return CorpusTopicIndex(corpus, model, dictionary, txt2tokens).id


class CorpusTopicIndex(IdComposer):
    '''Inferred topic model topics for texts in a corpus. '''

    def __init__(self, corpus, model, dictionary=None, txt2tokens=None):
        self.corpus, self.model = resolveIds(corpus, model)
        self.dictionary, self.text2tokens = resolveIds(dictionary, txt2tokens)
        IdComposer.__init__(self, attributes=['corpus', 'model', 'dictionary', 'text2tokens'])

    # todo implement __equals__

    def textTopics(self, textId):
        '''
        :return: topics for given texts, map of topicId -> topic value,
                probably a vector of floats.
        '''
        cind = self.corpus_index
        tvec = self.__topics[cind.id2index(textId)]
        return { tid: tvec[i] for tid, i in self.__id2ind.iteritems() }

    @property
    def corpus_index(self):
        if not hasattr(self, '_cindex'):
            cindBuild = resolve('corpus_index_builder')
            self._cindex = cindBuild(self.corpus)
        return self._cindex

    def __len__(self): return len(self.__topics)

    def __indexIds(self):
        ''' Array of ids from corpus index, in the same order. '''
        if not hasattr(self, '_textIds'):
            self._textIds = np.array([id for id in self.corpus_index], dtype=np.object)
        return self._textIds

    def topicMatrix(self):
        '''
        :return: ndarray of document-topic distributions
            rows indices correspond to text indices contained in self.corpus_index
        '''
        if self.normalized: return self._ntopics
        else: return self.__topics

    def normalize(self, norm=True):
        '''
        normalize document-topic matrix rows to probability distributions (1.0 sum)
        :return:
        '''
        self._normalized = norm
        if norm:
            from sklearn.preprocessing import normalize
            self._ntopics = normalize(self.__topics, norm='l1')

    @property
    def normalized(self):
        if hasattr(self, '_normalized'): return self._normalized
        else: return False

    def topicTexts(self, topicId, sorted='desc', top=None):
        '''
        :param topicId:
        :param sorted: 'desc', 'asc', or None (do not sort)
        :param top: if sorting, return this many texts from start of the sorted list
        :return: ndarray with rows containing textId, topicWeight pairs
        '''
        tind = self.__id2ind[topicId]
        tmatrix = self.__topics if not self.normalized else self._ntopics
        topics = tmatrix[:, tind]
        ids = self.__indexIds()
        if sorted is not None:
            if sorted == 'desc': sind = np.argsort(-topics)
            elif sorted == 'asc': sind = np.argsort(topics)
            else: raise Exception('invalid sorted argument: %s'%sorted)
            if top is not None:
                if top < len(sind): sind = sind[:top]
            topics = topics[sind]
            ids = ids[sind]
        res = np.empty((len(topics), 2), dtype=np.object)
        for i, id_ in enumerate(ids):
            res[i, 0], res[i, 1] = id_, topics[i]
        return res

    #### build/save/load interface

    # requires: bow_corpus_builder
    def __buildOld(self):
        model, corpus = resolve(self.model, self.corpus)
        txt2tok = resolve(self.text2tokens if self.text2tokens else model.text2tokens)
        dict = resolve(self.dictionary if self.dictionary else model.dictionary)
        self.__createTopicIdIndex()
        # turn corpus 2 bow corpus, make corpus index
        bowBuilder = resolve('bow_corpus_builder')
        bowCorpus = bowBuilder(corpus, txt2tok, dict)
        self.__topics = np.zeros((len(bowCorpus), model.numTopics()), dtype=np.float32)
        for i, bowTxt in enumerate(bowCorpus):
            tvec = model.inferTopics(bowTxt, format='bow')
            for tid, ti in self.__id2ind.iteritems():
                self.__topics[i, ti] = tvec[tid]

    def _logger(self):
        if not hasattr(self, '_log'):
            self._log = createLogger(fullClassName(self), INFO)
        return self._log

    # requires: bow_corpus_builder, corpus_index_builder
    def build(self):
        model = resolve(self.model)
        storedVectorsUsed = False
        if self._useNativeVectorization():
            textTopics = model.corpusTopicVectors()
            if textTopics is not None:
                # todo: test for this case
                ci = resolve('corpus_index_builder')(self.corpus)
                shape = (len(ci), model.numTopics())
                # todo maybe use == to compare indices (speed issue)
                if shape == textTopics.shape:
                    self.__topics = np.copy(textTopics)
                    storedVectorsUsed = True
                    # todo remove __id2ind variable from the class
                    self.__id2ind = { id_:i for i, id_ in enumerate(model.topicIds()) }
                else:
                    self._logger().info('corpusTopicVectors shape mismatch, '
                                        'stored %s, required %s \n'
                                        'proceeding to infer text topics' % (textTopics.shape, str(shape)))
        if not storedVectorsUsed:
            corpus = resolve(self.corpus)
            txt2tok = resolveIds(self.text2tokens if self.text2tokens else model.text2tokens)
            dict = resolveIds(self.dictionary if self.dictionary else model.dictionary)
            # turn corpus 2 bow corpus, make corpus index
            bowBuilder = resolve('bow_corpus_builder')
            bowCorpus = bowBuilder(corpus, txt2tok, dict)
            self.__topics = np.zeros((len(bowCorpus), model.numTopics()), dtype=np.float32)
            self.__createTopicIdIndex()
            tvec = model.inferTopics(bowCorpus, batch=True, format='bow')
            for i, txtVec in enumerate(tvec):
                 for tid, ti in self.__id2ind.iteritems():
                     self.__topics[i, ti] = txtVec[tid]

    def _topics2vector(self, tvec):
        '''
        Convert a map: topicId -> topicWeight to a ndarray of topic weights,
        where topic indexes are indexed by self.__createTopicIdIndex
        :param tvec: topic weights
        '''
        #TODO: call self.__createTopicIdIndex(), rename __id2ind
        vec = np.zeros(len(self.__id2ind))
        for tid, ti in self.__id2ind.iteritems():
            vec[ti] = tvec[tid]
        return vec

    def _useNativeVectorization(self):
        '''
        Determine weather the index building params match the model building params
         and allow to use of text vectors stored in the model, if they exist.
        '''
        # corpora, dictionaries and tokenization must match, else
        #  existing model-stored text vectors could differ from
        #  vectorizations of text derived from params of topic index
        model = resolve(self.model)
        if resolveId(self.corpus) == resolveId(model.corpus) \
            and (not self.dictionary or \
                resolveId(self.dictionary) == resolveId(model.dictionary)) \
            and (not self.text2tokens or \
                 resolveId(self.text2tokens) == resolveId(model.text2tokens)):
            return True
        else: return False

    def __createTopicIdIndex(self):
        '''
        Since topic ids can in general be any objects, mapping between
        ids and indices [0, ... , NumTopics] must be created.
        '''
        model = resolve(self.model)
        self.__id2ind = { tid: i for i, tid in enumerate(model.topicIds()) }

    def __getstate__(self):
        return IdComposer.__getstate__(self), self.__id2ind

    def __setstate__(self, state):
        IdComposer.__setstate__(self, state[0])
        self.__id2ind = state[1]

    def save(self, folder):
        pickleObject(self, folder)
        np.save(self.__topicVectorsFname(folder), self.__topics)

    def load(self, folder):
        self.__topics = np.load(self.__topicVectorsFname(folder))

    def __topicVectorsFname(self, f):
        return path.join(f, 'corpusTopicVectors.npy')


