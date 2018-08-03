from pytopia.context.ContextResolver import resolve
from pytopia.measure.topic_distance import cosine
from pytopia.tools.IdComposer import IdComposer
from pytopia.topic_functions.coherence.doc_coh_factory import distance_coherence

class CoherenceFunctionBuilder(IdComposer):
    '''
    Builds topic coherence functions from a set of parameters.
    '''

    def __init__(self, type, vectors=None, threshold=None, topWords=10,
                    corpus='us_politics', text2tokens='RsssuckerTxt2Tokens',
                    dict='us_politics_dict', cache=None,
                    **params):
        self.type, self.vectors, self.threshold = type, vectors, threshold
        self.__p = params
        attrs = ['type', 'vectors', 'threshold']
        for k, v in params.iteritems():
            setattr(self, k, v)
            attrs.append(k)
        self.topWords = topWords
        IdComposer.__init__(self, attributes=attrs, class_='Coherence')
        self.corpus, self.text2tokens, self.dictionary = corpus, text2tokens, dict
        self.cache = cache

    def __call__(self):
        self.buildScorer()
        if self.cache is None: return self.__scorer
        else: return self.__cachedScorer()

    def __cachedScorer(self):
        from pytopia.topic_functions.cached_function import CachedFunction
        import os
        from os import path
        if not path.exists(self.cache): os.mkdir(self.cache)
        return CachedFunction(self.__scorer, cacheFolder=self.cache, saveEvery=10)

    def buildScorer(self):
        if self.vectors is not None: self.__docVectorizer()
        if self.type in ['variance', 'avg-dist']: self.__distanceScorer()
        elif self.type == 'density': self.__densityScorer()
        elif self.type == 'graph': self.__graphScorer()
        elif self.type in ['npmi', 'uci', 'umass', 'c_a', 'c_p', 'c_v']:
            self.__palmettoScorer()
        elif self.type == 'text_distribution': self.__textDistribScorer()
        else: raise Exception('unknown algorithm type: %s'%self.type)
        return self.__scorer

    def __palmettoScorer(self):
        from pytopia.topic_functions.coherence.palmetto_coherence import PalmettoCoherence
        if 'standard' in self.__p and self.__p['standard'] == True:
            # for 'standard' palmetto, original index stores regular words, not stems
            # so inverse tokenization has to be performed
            itb = resolve('inverse_tokenizer_builder')
            itok = itb(self.corpus, self.text2tokens, True)
        else: itok = None
        coh = PalmettoCoherence(self.type, topWords=self.topWords,
                                wordTransform=itok, **self.__p)
        self.__scorer = coh

    def __textDistribScorer(self):
        from pytopia.topic_functions.coherence.document_distribution import DocuDistCoherence
        self.__scorer = DocuDistCoherence(cosine)
        #self.__scorer = DocuDistCoherence(kullbackLeibler)

    def __distanceScorer(self):
        self.__scorer = \
            distance_coherence(self.type, self.threshold,
                               mapper=self.mapper, mapperIsFactory=self.mapperIsFactory,
                               **self.__p)

    def __densityScorer(self):
        from pytopia.topic_functions.coherence.density_coherence import GaussCoherence
        from pytopia.topic_functions.document_selectors import TopDocSelector
        from pytopia.topic_functions.topic_documents_score import TopicDocumentsScore
        select = TopDocSelector(self.threshold)
        score = GaussCoherence(**self.__p)
        self.__scorer = TopicDocumentsScore(selector=select, score=score,
                                            mapper=self.mapper,
                                            mapperIsFactory=self.mapperIsFactory)

    def __graphScorer(self):
        from pytopia.topic_functions.coherence.doc_coh_factory import graph_coherence
        self.__scorer = \
            graph_coherence(self.threshold, mapper=self.mapper, mapperIsFactory=self.mapperIsFactory,
                            **self.__p)

    def __docVectorizer(self):
        '''
        Based on self.vectors parameter, create 'mapper' component for TopicElementScore,
        and 'mapperIsFactory' param. Write these params in self.__p dict.
        '''
        if self.vectors == 'tf-idf':
            mapper = resolve('corpus_tfidf_builder')
            mapperIsFactory = True
        elif self.vectors == 'probability':
            from pytopia.resource.text_prob_vector.TextProbVectorizer import TextProbVectorizer
            vectorizer = TextProbVectorizer(text2tokens=self.text2tokens, dictionary=self.dictionary)
            textVectors = resolve('corpus_text_vectors_builder')\
                            (vectorizer=vectorizer, corpus=self.corpus)
            mapper = textVectors
            mapperIsFactory = False
        elif self.vectors in ['word2vec', 'glove', 'word2vec-avg', 'glove-avg',
                              'word2vec-cro', 'glove-cro', 'word2vec-cro-avg', 'glove-cro-avg']:
            from pytopia.resource.word_vec_aggregator.WordVecAggregator import WordVecAggregator
            w2vec, glove = self.vectors.startswith('word2vec'), self.vectors.startswith('glove')
            cro = '-cro' in self.vectors
            if w2vec:
                if not cro:
                    embeddings = resolve('word2vec_builder')('GoogleNews-vectors-negative300.bin')
                else: embeddings = resolve('word2vec_builder')('word2vec.hrwac.cbow.vectors.bin')
            elif glove:
                if not cro:
                    embeddings = resolve('glove_vectors_builder')('glove.6B.300d.txt')
                else:
                    embeddings = resolve('glove_vectors_builder')('glove.hrwac.300d.txt')
            else:
                raise Exception('unknown vectors: %s' % self.vectors)
            avg = True if self.vectors.endswith('avg') else None
            if not cro: txt2tok = 'alphanum_gtar_stopword_tokenizer'
            else: txt2tok = 'croelect_alphanum_stopword_tokenizer'
            text2vec = WordVecAggregator(txt2tok, embeddings, None, avg)
            mapper = resolve('corpus_text_vectors_builder')(vectorizer=text2vec, corpus=self.corpus)
            mapperIsFactory = False
        self.mapper, self.mapperIsFactory = mapper, mapperIsFactory
