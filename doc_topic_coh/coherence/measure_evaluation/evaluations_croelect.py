from doc_topic_coh.coherence.measure_evaluation.evaluations import *
from doc_topic_coh.coherence.tools import IdList
from doc_topic_coh.dataset.croelect_topics import croelectTopicsLabeled
from doc_topic_coh.resources.croelect_resources.noncorpus_resources import corpusId, dictId, text2tokensId

croelectParams = [{ 'corpus':corpusId, 'text2tokens':text2tokensId, 'dict':dictId }]
croelectTopics = croelectTopicsLabeled()


croThresholds = {
    ('tf-idf','cosine'): [0.93172, 0.95288, 0.96521, 0.97884, 0.98909, 0.99639, ] ,
    ('tf-idf','l2'): [1.36508, 1.38049, 1.38939, 1.39917, 1.40648, 1.41166, ],
    ('tf-idf','l1'): [11.30759, 12.51893, 13.68560, 15.78645, 18.28902, 21.00582, ],
    ('probability','cosine'): [0.89012, 0.93276, 0.95462, 0.97487, 0.98792, 0.99612, ],
    ('probability','l2'): [0.11922, 0.12929, 0.13854, 0.15582, 0.17922, 0.20827, ],
    ('probability','l1'): [1.86245, 1.89926, 1.92199, 1.95040, 1.97360, 1.99029, ],
    ('word2vec','cosine'): [0.27147, 0.34379, 0.41284, 0.53914, 0.68173, 0.82151, ],
    ('word2vec','l2'): [475.81082, 584.88586, 699.39337, 922.47156, 1252.02527, 1721.08252, ],
    ('word2vec','l1'): [6565.63867, 8061.64111, 9636.98633, 12706.73730, 17234.92188, 23676.13281, ],
    ('word2vec-avg', 'l2'): [3.14411, 3.51542, 3.87957, 4.50022, 5.26021, 6.11886, ],
    ('word2vec-avg', 'l1'): [43.37675, 48.50849, 53.46702, 61.97827, 72.42890, 84.26587, ],
    ('glove', 'cosine'): [0.08100, 0.09782, 0.11514, 0.15029, 0.20064, 0.26623, ],
    ('glove', 'l2'): [62.39438, 77.37844, 93.24452, 126.50224, 181.59282, 270.50101, ],
    ('glove', 'l1'): [860.78955, 1067.40625, 1285.85107, 1742.93213, 2495.15991, 3710.93481, ],
    ('glove-avg', 'l2'): [0.39617, 0.43631, 0.47386, 0.54599, 0.64200, 0.76677, ],
    ('glove-avg', 'l1'): [5.48346, 6.03018, 6.55145, 7.54620, 8.87531, 10.59987, ],
}

def croelectize(p):
    '''
    Modify parameters of a coherence measure to work with croelect dataset,
    modifying resource-related params
    :param p: map of param name -> param value
    :return: copy of p with added and modified param values
    '''
    from copy import deepcopy
    p = deepcopy(p)
    # basic resources
    croelectResParams = {'corpus': corpusId, 'text2tokens': text2tokensId, 'dict': dictId}
    for k,v in croelectResParams.iteritems(): p[k] = v
    if 'weightFilter' in p:
        # this can change for emb, so record now
        vecs, dist = p['vectors'], p['distance'].__name__
    # embedding vectors names
    if 'vectors' in p:
        vp = p['vectors']
        if 'word2vec' in vp or 'glove' in vp:
            if 'avg' in vp: p['vectors'] = vp.replace('avg', 'cro-avg')
            else: p['vectors'] = vp + '-cro'
    # edge thresholds
    if 'weightFilter' in p:
        from doc_topic_coh.coherence.measure_evaluation.model_selection import thresholds
        threshold = p['weightFilter'][1]
        th = thresholds[(vecs, dist)]
        croTh = croThresholds[(vecs, dist)]
        found = False
        for i, t in enumerate(th):
            if t == threshold:
                p['weightFilter'][1] = croTh[i]
                found = True
                break
        if not found: raise Exception('threshold not found: %g, %s, %s'%(threshold, vecs, dist))
    return p

def croelectizeParamset(paramset):
    cp = IdList(); cp.id = paramset.id + '_croelectized'
    for p in paramset: cp.append(croelectize(p))
    return cp

def bestParamsDocCroelect():
    from doc_topic_coh.coherence.measure_evaluation.evaluations import bestParamsDoc
    return croelectizeParamset(bestParamsDoc(bline=True))

def palmettoBestCrowiki():
    '''
    Measures from the paper "Exploring the Space of Topic Coherence Measures",
    configured to use croatian wikipedia for co-occurrence counts.
    '''
    params = [
                { 'type':'npmi', 'standard': False, 'index': 'crowiki_palmetto_index', 'windowSize': 10},
                { 'type':'uci', 'standard': False, 'index': 'crowiki_palmetto_index', 'windowSize': 10},
                { 'type':'c_a', 'standard': False, 'index': 'crowiki_palmetto_index', 'windowSize': 5},
                { 'type':'c_v', 'standard': False, 'index': 'crowiki_palmetto_index', 'windowSize': 110},
                { 'type':'c_p', 'standard': False, 'index': 'crowiki_palmetto_index', 'windowSize': 70},
            ]
    p = IdList(params);
    p.extend(docudistBlineParam())
    p.id = 'palmetto_best_cro'
    return p

from doc_topic_coh.coherence.measure_evaluation.utils import subsampleList

def bestDocCohOnTestcro(subsample=None):
    topics = subsampleList(croelectTopics, subsample) if subsample else croelectTopics
    experiment(bestParamsDocCroelect(), action='run',
               topics=topics, posClass=['theme', 'theme_noise'])
    experiment(bestParamsDocCroelect(), action='signif',
               topics=topics, posClass=['theme', 'theme_noise'])

def bestWordCohOnTestcro(subsample=None):
    topics = subsampleList(croelectTopics, subsample) if subsample else croelectTopics
    experiment(palmettoBestCrowiki(), action='run',
               topics=topics, posClass=['theme', 'theme_noise'])
    experiment(palmettoBestCrowiki(), action='signif',
               topics=topics, posClass=['theme', 'theme_noise'])

if __name__ == '__main__':
    bestDocCohOnTestcro() # Table 4, test-cro
    #bestWordCohOnTestcro() # Table 6, test-cro