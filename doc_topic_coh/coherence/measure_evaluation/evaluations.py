from doc_topic_coh.dataset.topic_splits import devTestSplit
from doc_topic_coh.coherence.measure_evaluation.utils import experiment
from doc_topic_coh.coherence.tools import flattenParams as fp, joinParams as jp, IdList
from pytopia.measure.topic_distance import cosine, l1, l2

from doc_topic_coh.coherence.measure_evaluation.utils import experiment

dev, test = devTestSplit()

bestDocCohModel = { 'distance': cosine, 'weighted': False, 'center': 'mean',
         'algorithm': 'communicability', 'vectors': 'tf-idf',
         'threshold': 50, 'weightFilter': [0, 0.92056], 'type': 'graph' }

docCohBaseline = {'type':'text_distribution'}
def docudistBlineParam():
    p = IdList([ docCohBaseline ])
    p.id = 'docu_dist_baseline'
    return p

bestDocCohMeasure = {'distance': cosine, 'weighted': False, 'center': 'mean',
                     'algorithm': 'communicability', 'vectors': 'tf-idf',
                     'threshold': 50, 'weightFilter': [0, 0.92056], 'type': 'graph'},

def bestParamsDoc(bline=True):
    p = [
        {'distance': cosine, 'center': 'mean', 'vectors': 'probability', 'exp': 1.0,
         'threshold': 50, 'type': 'variance'},
        {'distance': cosine, 'center': 'mean', 'vectors': 'glove',
         'exp': 1.0, 'threshold': 25, 'type': 'variance'},
        {'distance': cosine, 'weighted': False, 'center': 'mean',
         'algorithm': 'communicability', 'vectors': 'tf-idf',
         'threshold': 50, 'weightFilter': [0, 0.92056], 'type': 'graph'},
        {'distance': l1, 'weighted': True, 'center': 'mean', 'algorithm': 'clustering',
         'vectors': 'glove-avg', 'threshold': 25, 'weightFilter': [0, 14.31248], 'type': 'graph'},
        {'center': 'mean', 'vectors': 'tf-idf', 'covariance': 'spherical',
         'dimReduce': None, 'threshold': 50, 'type': 'density'},
        {'center': 'mean', 'vectors': 'word2vec-avg', 'covariance': 'spherical',
         'dimReduce': 10, 'threshold': 25, 'type': 'density'}
    ]
    pl = IdList(p); pl.id = 'best_doc'
    if bline:
        pl += docudistBlineParam()
        pl.id += '_baselined'
    return pl

# word coherence selected as representative, for various experiments
palmettoCp = { 'type':'c_p', 'standard': False, 'index': 'wiki_docs', 'windowSize': 70}

def palmettoWordCoherence(docBaseline=False):
    '''
    Best-performing word-based measures from the Palmetto library
    (measures from the paper "Exploring the Space of Topic Coherence Measures")
    :param docBaseline: if true, add document-based baseline to param set
    '''
    params = [
                { 'type':'npmi', 'standard': False, 'index': 'wiki_docs', 'windowSize': 10},
                { 'type':'uci', 'standard': False, 'index': 'wiki_docs', 'windowSize': 10},
                { 'type':'c_a', 'standard': False, 'index': 'wiki_docs', 'windowSize': 5},
                { 'type':'c_v', 'standard': False, 'index': 'wiki_docs', 'windowSize': 110},
                { 'type':'c_p', 'standard': False, 'index': 'wiki_docs', 'windowSize': 70},
            ]
    p = IdList(params); p.id = 'palmetto_best'
    if docBaseline:
        p.append(docCohBaseline)
        p.id += '_doc_blined'
    return p

from doc_topic_coh.coherence.measure_evaluation.utils import subsampleList

def wordCohOnTest(subsample=None):
    topics = subsampleList(test, subsample) if subsample else test
    experiment(palmettoWordCoherence(True), topics=topics, action='run')
    experiment(palmettoWordCoherence(True), topics=topics, action='signif')

def bestDocCohOnTest(subsample=None):
    topics = subsampleList(test, subsample) if subsample else test
    experiment(bestParamsDoc(), topics=topics, action='run')
    experiment(bestParamsDoc(), topics=topics, action='signif')

if __name__ == '__main__':
    bestDocCohOnTest() # Table 4, test
    #wordCohOnTest() # Table 6, test
