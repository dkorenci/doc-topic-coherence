from pytopia.resource.corpus_tfidf.CorpusTfidfIndex import CorpusTfidfBuilder
from pytopia.topic_functions.coherence.avg_dist_coherence import \
    AverageVectorDistCoh
from pytopia.topic_functions.coherence.variance_coherence import VarianceCoherence
from pytopia.topic_functions.document_selectors import *
from pytopia.topic_functions.topic_documents_score import TopicDocumentsScore
from pytopia.measure.topic_distance import cosine, l1, l2

def distance_coherence(type, threshold, mapper, distance,
                       center='mean', exp=1.0, timer=False,
                       mapperIsFactory=True):
    '''
    Builds distance (variance- or avg.distance) topic coherence calculator.
    :param type: either 'variance', 'avg-dist'
    '''
    if type == 'variance': coh = VarianceCoherence(distance, center, exp)
    elif type == 'avg-dist': coh = AverageVectorDistCoh(distance, center, exp)
    else: raise Exception('unsupported type: %s'%type)
    select = TopDocSelector(threshold)
    c = TopicDocumentsScore(selector=select, mapper=mapper,
                            score=coh, timer=timer, mapperIsFactory=mapperIsFactory)
    return c

def variance_coherence(threshold, mapperCreator, distance,
                       center='mean', exp=1.0, timer=False, factory=True):
    if distance == 'l1': d = l1
    elif distance == 'l2': d = l2
    elif distance == 'cosine': d = cosine
    else: raise Exception('Unsupported distance %s' % distance)
    select = TopDocSelector(threshold)
    coh = VarianceCoherence(d, center, exp)
    if mapperCreator is None: mapperCreator = CorpusTfidfBuilder()
    c = TopicDocumentsScore(selector=select, mapper=mapperCreator,
                            score=coh, timer=timer, mapperIsFactory=factory)
    return c

def avg_dist_coherence(threshold, mapperCreator, distance,
                       center='mean', exp=1.0, factory=True):
    if distance == 'l1': d = l1
    elif distance == 'l2': d = l2
    elif distance == 'cosine': d = cosine
    else: raise Exception('Unsupported distance %s' % distance)
    score = AverageVectorDistCoh(d, center, exp)
    if mapperCreator is None: mapperCreator = CorpusTfidfBuilder()
    c = TopicDocumentsScore(selector = TopDocSelector(threshold),
                            mapper= mapperCreator, score = score, mapperIsFactory=factory)
    return c

from pytopia.topic_functions.coherence.graph_coherence import GraphCoherence
def graph_coherence(threshold, mapper, distance, weightFilter=None,
                    weighted=True, algorithm='clustering', center='mean',
                    mapperIsFactory=True):
    if mapper is None: mapper = CorpusTfidfBuilder()
    c = GraphCoherence(selector = TopDocSelector(threshold), mapper=mapper,
                       metric=distance, weightFilter=weightFilter, weighted=weighted,
                       algorithm=algorithm, center=center, mapperIsFactory=mapperIsFactory)
    return c