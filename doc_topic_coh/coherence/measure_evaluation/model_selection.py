from doc_topic_coh.dataset.topic_splits import devTestSplit
from doc_topic_coh.coherence.measure_evaluation.utils import experiment, assignVectors
from doc_topic_coh.coherence.tools import flattenParams as fp, joinParams as jp, IdList
from pytopia.measure.topic_distance import cosine, l1, l2

docSelectParams = { 'threshold': [10, 25, 50, 100] }
docSelectParams = fp(docSelectParams)

distanceMeasures = [cosine, l1, l2]

dev, test = devTestSplit()

def distanceParams(vectors=None):
    params = {
              'type': ['variance', 'avg-dist'],
              'vectors': None,
              'distance': distanceMeasures,
              'center': 'mean',
              'exp': 1.0
              }
    p = IdList(jp(fp(params), docSelectParams))
    p.id = 'distance_params'
    p = assignVectors(p, vectors)
    return p

thresholds = {
    ('tf-idf','cosine'): [0.92056, 0.94344, 0.95661, 0.97246, 0.98525, 0.99478, ] ,
    ('tf-idf','l2'): [1.35688, 1.37364, 1.38319, 1.39460, 1.40374, 1.41052, ] ,
    ('tf-idf','l1'): [9.52592, 10.83310, 12.14663, 14.50215, 17.43981, 20.59608, ],
    ('probability','cosine'): [0.87706, 0.92783, 0.95097, 0.97251, 0.98635, 0.99536, ],
    ('probability','l2'): [0.12387, 0.13656, 0.14878, 0.17092, 0.20064, 0.23936, ],
    ('probability','l1'): [1.84746, 1.88496, 1.90951, 1.94139, 1.96886, 1.98925, ],
    ('word2vec','cosine'): [0.10344, 0.12718, 0.15091, 0.19408, 0.24799, 0.30865, ],
    ('word2vec','l2'): [58.13322, 78.54189, 101.04961, 146.47849, 225.47549, 334.48654, ],
    ('word2vec','l1'): [804.65845, 1087.80811, 1398.32141, 2030.68066, 3133.24609, 4659.37695, ],
    ('glove', 'cosine'): [0.05979, 0.07508, 0.09090, 0.12111, 0.16095, 0.20816, ],
    ('glove', 'l2'): [158.14783, 216.73793, 282.91806, 424.81396, 671.20081, 1034.27319, ],
    ('glove', 'l1'): [2015.83020, 2680.55078, 3449.74219, 4973.33984, 7456.08691, 10653.34375, ],
}


def distanceParams(vectors):
    if vectors == 'corpus':
        params = {
                  'type': ['variance', 'avg-dist'],
                  'vectors': ['tf-idf', 'probability'],
                  'distance': distanceMeasures,
                  'center': 'mean',
                  'exp': 1.0
                  }
        p = IdList(jp(fp(params), docSelectParams))
    elif vectors == 'world':
        params = {
                  'type': ['variance', 'avg-dist'],
                  'vectors': ['word2vec', 'glove'],
                  'distance': cosine,
                  'center': 'mean',
                  'exp': 1.0
                  }
        p = IdList(jp(fp(params), docSelectParams))
        params = {
                  'type': ['variance', 'avg-dist'],
                  'vectors': ['word2vec', 'glove', 'word2vec-avg', 'glove-avg'],
                  'distance': [l1, l2],
                  'center': 'mean',
                  'exp': 1.0
                  }
        p += jp(fp(params), docSelectParams)
    p.id = 'distance_params_%s_vectors' % vectors
    return p

thresholds = {
    ('tf-idf','cosine'): [0.92056, 0.94344, 0.95661, 0.97246, 0.98525, 0.99478, ] ,
    ('tf-idf','l2'): [1.35688, 1.37364, 1.38319, 1.39460, 1.40374, 1.41052, ] ,
    ('tf-idf','l1'): [9.52592, 10.83310, 12.14663, 14.50215, 17.43981, 20.59608, ],
    ('probability','cosine'): [0.87706, 0.92783, 0.95097, 0.97251, 0.98635, 0.99536, ],
    ('probability','l2'): [0.12387, 0.13656, 0.14878, 0.17092, 0.20064, 0.23936, ],
    ('probability','l1'): [1.84746, 1.88496, 1.90951, 1.94139, 1.96886, 1.98925, ],
    ('word2vec','cosine'): [0.10344, 0.12718, 0.15091, 0.19408, 0.24799, 0.30865, ],
    ('word2vec','l2'): [58.13322, 78.54189, 101.04961, 146.47849, 225.47549, 334.48654, ],
    ('word2vec','l1'): [804.65845, 1087.80811, 1398.32141, 2030.68066, 3133.24609, 4659.37695, ],
    ('word2vec-avg', 'l2'): [0.38106, 0.42444, 0.46448, 0.53258, 0.61361, 0.70335, ],
    ('word2vec-avg', 'l1'): [5.25766, 5.87006, 6.42045, 7.36616, 8.48549, 9.73404, ],
    ('glove', 'cosine'): [0.05979, 0.07508, 0.09090, 0.12111, 0.16095, 0.20816, ],
    ('glove', 'l2'): [158.14783, 216.73793, 282.91806, 424.81396, 671.20081, 1034.27319, ],
    ('glove', 'l1'): [2015.83020, 2680.55078, 3449.74219, 4973.33984, 7456.08691, 10653.34375, ],
    ('glove-avg', 'l2'): [0.94280, 1.05602, 1.16246, 1.34349, 1.55822, 1.79130, ],
    ('glove-avg', 'l1'): [12.79924, 14.31248, 15.72214, 18.15014, 20.99771, 24.09225, ],
}

def thres2perc(vectors, distance, thVal):
    '''
    Converts value of distance threshold to corresponding percentile.
    '''
    # from distance_distribution.py , percentiles for which thresholds were printed
    threshPercs = [0.02, 0.05, 0.1, 0.25, 0.5, 0.75]
    for i, th in enumerate(thresholds[(vectors, distance)]):
        if thVal == th: return threshPercs[i]

def graphParams(vectors, distance):
    basic = { 'type':'graph', 'vectors': vectors, 'distance': distance }
    # Graph building with thresholding
    th = thresholds[(vectors, distance.__name__)]
    weightFilter = [[0, t] for t in th]
    thresh = {
             'algorithm': ['clustering', 'closeness'],
             'weightFilter': weightFilter,
             'weighted': [True, False],
             'center': 'mean',
    }
    threshNonWeighted = {
             'algorithm': ['communicability', 'num_connected'],
             'weightFilter': weightFilter,
             'weighted': False,
             'center': 'mean'
    }
    # Graph building without thresholding
    nothresh = {
            'algorithm': ['closeness', 'mst', 'clustering'],
            'weightFilter': None, 'weighted': True,
            'center': 'mean'
    }
    p = jp(fp(basic), fp(thresh)) + jp(fp(basic), fp(threshNonWeighted)) + jp(fp(basic), fp(nothresh))
    p = IdList(jp(p, docSelectParams))
    # label parameter set as either 'world' or 'corpus'
    if vectors in ['word2vec', 'glove', 'word2vec-avg', 'glove-avg']: vecLabel = 'world'
    elif vectors in  ['tf-idf', 'probability']: vecLabel = 'corpus'
    p.id = 'graph_params_%s_vectors' % vecLabel
    return p

def runGridGraphCorpus(action='run', topics=dev):
    if action == 'print':
        experiment(graphParams('tf-idf', cosine), action=action, topics=topics)
    else:
        experiment(graphParams('tf-idf', cosine), topics=topics)
        experiment(graphParams('tf-idf', l1), topics=topics)
        experiment(graphParams('tf-idf', l2), topics=topics)
        experiment(graphParams('probability', cosine), topics=topics)
        experiment(graphParams('probability', l1), topics=topics)
        experiment(graphParams('probability', l2), topics=topics)

def runGridGraphWorld(action='run', topics=dev):
    if action == 'print':
        experiment(graphParams('word2vec', cosine), action='print', topics=topics)
    else:
        experiment(graphParams('word2vec', cosine), topics=topics)
        experiment(graphParams('word2vec', l1), topics=topics)
        experiment(graphParams('word2vec-avg', l1), topics=topics)
        experiment(graphParams('word2vec', l2), topics=topics)
        experiment(graphParams('word2vec-avg', l2), topics=topics)
        experiment(graphParams('glove', cosine), topics=topics)
        experiment(graphParams('glove', l1), topics=topics)
        experiment(graphParams('glove-avg', l1), topics=topics)
        experiment(graphParams('glove', l2), topics=topics)
        experiment(graphParams('glove-avg', l2), topics=topics)

def densityParams(vectors):
    if vectors == 'world':
        # world vectors are max. 300 in size, so they need
        # to be reduced to a dimension << 100
        dimReduce = [None, 5, 10, 20]
    elif vectors == 'corpus':
        dimReduce = [None, 5, 10, 20, 50, 100]
    basic = {
                'type': 'density',
                'covariance': ['diag', 'spherical'],
                'center': 'mean',
                'dimReduce': dimReduce
            }
    basic = IdList(jp(fp(basic), docSelectParams))
    basic.id = 'density_params'
    basic = assignVectors(basic, vectors)
    return basic

def runGridDistance(vectors, action='run', topics=dev):
    experiment(distanceParams(vectors), topics=topics, action=action)

def runGridDensity(vectors, action='run', topics=dev):
    experiment(densityParams(vectors), action=action, topics=topics)

def evalTopValues(algo, vectors, plot=False):
    if algo == 'distance':
        experiment(distanceParams(vectors), action='eval',
                   evalTopics=test, evalPerc=0.95, plotEval=plot)
    elif algo == 'graph':
        if vectors == 'corpus':
            experiment(graphParams('tf-idf', cosine), action='eval',
                       evalTopics=test, evalPerc=0.95, plotEval=plot)
        elif vectors == 'world':
            experiment(graphParams('word2vec', cosine), action='eval',
                       evalTopics=test, evalPerc=0.95, plotEval=plot)
    elif algo == 'gauss':
        experiment(densityParams(vectors), action='eval', evalTopics=test,
                   evalPerc=0.95, plotEval=plot)

def printTopSelected(algo, vectors):
    if algo == 'distance':
        if vectors == 'corpus':
            experiment(distanceParams(vectors), action='printTop',
                       evalTopics=test, evalPerc=0.95, evalThresh=0.744)
        elif vectors == 'world':
            experiment(distanceParams(vectors), action='printTop',
                       evalTopics=test, evalPerc=0.95, evalThresh=0.7316)
    elif algo == 'graph':
        if vectors == 'corpus':
            experiment(graphParams('tf-idf', cosine), action='printTop',
                       evalTopics=test, evalPerc=0.95, evalThresh='median', th2per=thres2perc)
        elif vectors == 'world':
            experiment(graphParams('word2vec', cosine), action='printTop',
                       evalTopics=test, evalPerc=0.95, evalThresh='median', th2per=thres2perc)
    elif algo == 'gauss':
        if vectors == 'corpus':
            experiment(densityParams(vectors), action='printTop',
                       evalTopics=test, evalPerc=0.95, evalThresh='median')
        elif vectors == 'world':
            experiment(densityParams(vectors), action='printTop',
                       evalTopics=test, evalPerc=0.95, evalThresh=0.715)

def evalAllOnTest(plot=False):
    '''
    Evaluate top development set measures on test and save results,
    for all the measure categories.
    '''
    for algo in ['graph', 'distance', 'gauss']:
        for vec in ['corpus', 'world']:
            evalTopValues(algo, vec, plot=plot)

def evalPrintAllOnTest():
    '''
    Evaluate top development set measures on test and print
    those measures with top test performance, for all the measure categories.
    '''
    for algo in ['graph', 'distance', 'gauss']:
        for vec in ['corpus', 'world']:
            printTopSelected(algo, vec)

def evaluateParamsOnDev(action='run', subsample=None, type=None):
    '''
    Evaluate measure parameters on the development set, ie
    construct the measures from parameter sets and evaluate measures.
    :param action: 'run' to evaluate, 'print' to print results
    :param subsample: if not None, size of dev subsample to run measures on, for testing
    :return:
    '''
    if subsample:
        from doc_topic_coh.coherence.measure_evaluation.utils import subsampleList
        evalTopics = subsampleList(dev, subsample)
    else: evalTopics = dev
    if not type or type.startswith('graph'):
        runGridGraphCorpus(action, evalTopics)
        runGridGraphWorld(action, evalTopics)
    if not type or type.startswith('distance'):
        runGridDistance('corpus', action, evalTopics)
        runGridDistance('world', action, evalTopics)
    if not type or type.startswith('density'):
        runGridDensity('corpus', action, evalTopics)
        runGridDensity('world', action, evalTopics)

if __name__ == '__main__':
    # model selection on the development test
    # evaluate sensible parameters for all the categories,
    #  top measures can be selected from the printout
    evaluateParamsOnDev('run')
    evaluateParamsOnDev('print')
    # run evaluation of top dev measures on test,
    #  for the representativness analysis, and param analysis (in supplementary)
    #evalAllOnTest(plot=False)
    #evalPrintAllOnTest()
    pass
