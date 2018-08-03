from pytopia.tools.IdComposer import IdComposer, deduceId
from pytopia.context.ContextResolver import resolve, resolveId

from time import time
from scipy.sparse import spmatrix

from pytopia.resource.topic_dist_vectorizer.TopicDistVectorizer import TopicDistVectorizer

class TopicDocumentsScore(IdComposer):
    '''
    Calculates a numeric score for a topic by first selecting
    topic-related documents, mapping them into vectors or scalars,
    and calculating the score based on the matrix/vector of transformed documents.
    '''

    def __init__(self, selector, mapper, score, mapperIsFactory=True, timer=False, useTopic=False):
        '''
        :param selector: returns list of documents for the topic
        :param mapper: a mapper function on (selected) topic documents,
                returning vectors or scalar,
                or alternatively a 'factory' - callable that accepts 'dictionary',
                'text2tokens' and 'corpus' parameters (attributes of
                 a topic model to which processed topic belongs) and
                builds such a mapper.
                This is for creating a customized mapper for each model.
        :param mapperIsFactory: if True treat mapper as a factory as described above
        :param score: score function on the matrix/vector of transformed documents
        :param useTopic: if True, topic is also sent as parameter to mapper
        '''
        self.selector, self.score = selector, deduceId(score)
        self.mapper = resolveId(mapper)
        IdComposer.__init__(self)
        self.__factory = mapperIsFactory
        self.__mapper = resolve(mapper)
        self.__score = score
        self.__timer = timer
        self.__useTopic = useTopic

    def __call__(self, topic):
        '''
        :param topic: (modelId, topicId)
        '''
        documents = self.selector(topic)
        mapper = self.__createMapper(topic) if self.__factory else self.__mapper
        transformed = []
        if self.__timer: print 'processing topic: ', topic
        for doc in documents:
            if self.__timer: t0 = time()
            if isinstance(mapper, TopicDistVectorizer):
                te = mapper(doc, model=topic[0])
            else: te = mapper(doc)
            transformed.append(te)
            if self.__timer:
                print 'processed doc %s in time: %.4f' % (str(doc), time()-t0)
                if isinstance(te, spmatrix): print '    num_non_zero', te.nnz
        if self.__timer: t0 = time()
        composed = self.__composeMatrixOrVector(transformed)
        if self.__timer:
            print 'matrix composed in %.4f' % (time()-t0)
            if isinstance(composed, spmatrix):
                print '     matrix num_non_zero', composed.nnz
        if self.__score is None: return composed
        else: return self.__score(composed)

    def __createMapper(self, topic):
        '''
        Create mapper by passing topic-related params such
        as topics model corpus and dictionary to the mapper creator.
        Cache results.
        :param topic: (modelId, topicId)
        :return:
        '''
        mid, tid = topic
        model = resolve(mid)
        params = { 'dictionary': model.dictionary,
                   'text2tokens': model.text2tokens,
                   'corpus': model.corpus }
        if not hasattr(self, '_mapperCache'): self._mapperCache = {}
        if str(params) not in self._mapperCache:
            self._mapperCache[str(params)] = self.__mapper(**params)
        return self._mapperCache[str(params)]

    def __composeMatrixOrVector(self, elements):
        '''
        :param elements: list-like of either vectors (all either sparse or ndarray
                        with same shape) or scalars
        :return: for vectors return matrix - sparse if all vectors are sparse,
                or dense (ndarray) matrix. for scalars return a vector.
        '''
        elements = [ e for e in elements if e is not None ]
        if not elements: return None
        from scipy.sparse import spmatrix, dok_matrix as sparse_type
        import numpy as np
        sparse = True; cols = None
        for e in elements:
            if isinstance(e, np.ndarray): sparse = False
            elif not isinstance(e, spmatrix):
                raise Exception('invalid vector type: %s' % type(e))
            colsNew = e.shape[1] if sparse else e.shape[0]
            if cols is None: cols = colsNew
            elif cols != colsNew:
                raise Exception('Mismatch in vector lengths: %d %d' % (cols, colsNew))
        rows = len(elements)
        if sparse:
            mx = sparse_type((rows, cols), dtype=np.float64)
            for i, e in enumerate(elements):
                setRowSparse(mx, i, e)
        else:
            mx = np.empty((rows, cols), dtype=np.float64)
            for i, e in enumerate(elements): mx[i] = e
        return mx

def setRowSparse(matrix, rowIndex, row):
    _, ca = row.nonzero()
    for i, c in enumerate(ca):
        matrix[rowIndex, c] = row[0, c]

