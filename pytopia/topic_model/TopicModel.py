from pytopia.topic_model.Topic import Topic
from pytopia.utils.print_ import topTopicWords

from pytopia.context.ContextResolver import resolve

from os import path
import numpy as np

def load_from_file(fileName):
    from lxml import objectify
    file = None
    try:
        file = open(fileName)
        xml_desc = ''.join(file.readlines())
        file.close()
        o = objectify.fromstring(xml_desc)
        return o
    finally:
        if file is not None: file.close()

class TopicModel(object):
    '''
    Interface a TopicModel-like should support.
    Additionaly, 'id', 'dictionary' and 'text2tokens' are mandatory attributes.
    'dictionary' and 'text2tokens' are either objects or ids.
    '''

    coreMethods = ['topicIds', 'numTopics', 'topic', 'topicVector']

    def topicIds(self):
        '''
        List of ids of the model's topics, commonly integers in
        range 0..numTopics,  but generally ids can be non-integer objects.
        The ordering of ids defines integer indices of topics
        in topic vectors, ie. document-topic vectors,
        therefore it has to be fixed both between calls, and if new topics
        are added the ordering of old topics' ids must be preserved.
        '''
        raise NotImplementedError

    def numTopics(self): raise NotImplementedError

    def topic(self, topicId):
        return Topic(self, topicId, self.topicVector(topicId))

    def topicVector(self, topicId): raise NotImplementedError

    def topicMatrix(self, dtype=None):
        tids = self.topicIds()
        if not tids: return
        tv = self.topicVector(tids[0])
        rows, cols = len(tids), len(tv)
        dtype = dtype if dtype else tv.dtype
        mtx = np.empty((len(tids), cols), dtype)
        for i, ti in enumerate(tids):
            mtx[i] = self.topicVector(ti)
        return mtx

    def corpusTopicVectors(self, txtId=None):
        '''
        Optional, if calculated and stored, return the matrix
        of text-topics vectors for texts in the corpus  used to build the models.
        The mapping of row indices to texts is defined
        by CorpusIndex used upon model build time.
        :param txtId: if None return the matrix, otherwise return text's vector.
        '''
        return None

    def topic2string(self, topicId, topw=10):
        return u' '.join(self.topTopicWords(topicId, topw))

    def topTopicWords(self, topicId, topw=10):
        v = self.topicVector(topicId)
        d = resolve(self.dictionary)
        return topTopicWords(v, d, topw)

    def __eq__(self, other):
        '''
        Basic topic-level equality of models.
        Concrete models should extend with specific features used for comparison.
        TODO: add corpus, dictionary and text2tokens to comparison?
        '''
        if self is other: return True
        if self.numTopics() != other.numTopics(): return False
        if sorted(self.topicIds()) != sorted(other.topicIds()): return False
        for ti in self.topicIds():
            ts, to = self.topicVector(ti), other.topicVector(ti)
            if not np.equal(ts, to).all(): return False
        return True

    def __getitem__(self, topicId):
        ''' Shortcut for self.topic(). '''
        return self.topic(topicId)

    def __iter__(self):
        ''' Iterate over topics. '''
        for tid in self.topicIds(): yield Topic(self, tid, self.topicVector(tid))

    def inferTopics(self, txt, batch=False, format='tokens'):
        '''
        Calculate document-topic proportions for text(s).
        :param txt: text or iterable of texts
        :param batch: it True, txt is iterable of text, otherwise a single text
        :param format of a single text:
            'tokens' - list of tokens, 'bow' - list of (wordId, wordCount), 'string'
        :return: If a single text, single doc-topic vector, else a list-like of vectors.
            A doc-topic vector is a mapping topicId -> inferredTopicValue.
        '''
        raise NotImplementedError

    def load(self, folder):
        '''
        Load additional generic resources associated with a topic model:
        load topic description from file and attach as 'description' attribute.
        '''
        descFile = path.join(folder, 'description.xml')
        if path.exists(descFile):
            self.description = load_from_file(descFile)
        else: self.description = None

    def save(self, folder): raise NotImplementedError

    def __str__(self):
        s=u'%s\n'%self.id
        s+='numTopics: %d\n' % self.numTopics()
        for tid in self.topicIds():
            s+='topic %.4d: %s\n' % (tid, self.topic2string(tid, 20))
        return s

import types
def isTopicModel(o):
    '''
    True if object o is a TopicModel or TopicModel-like (has core TM methods)
    '''
    if isinstance(o, TopicModel): return True
    else:
        for mn in TopicModel.coreMethods:
            if not(hasattr(o, mn) and isinstance(getattr(o, mn), types.MethodType)):
                return False
        return True