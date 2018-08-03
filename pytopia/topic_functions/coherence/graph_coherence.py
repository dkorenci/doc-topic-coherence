from pytopia.topic_functions.topic_documents_score import TopicDocumentsScore
from pytopia.tools.IdComposer import IdComposer, deduceId
from pytopia.context.ContextResolver import resolveId

import numpy as np
import networkx as nx

class GraphCoherence(IdComposer):
    '''
    Calculates topic coherence by extracting topic-related elements
    such as documents or words, constructing a graph with items as nodes,
    and then calculating a coherence measure of the graph.
    '''

    def __init__(self, selector, mapper, metric, weightFilter=None,
                 weighted=True, algorithm='clustering', center='mean',
                 mapperIsFactory=True):
        '''
        :param selector: selector of topic items (nodes of the graph)
        :param mapper: mapper of topic items to vectors
        :param metric: weight metric on pairs of vectors, for forming weight matrix
        :param weightFilter: if not None - pair/list of two elements
                    weights in weight matrix outside this interval will be set to 0
        :param weighted: if True, graph algorithms will work with weighted graphs
        :param algorithm: graph-based measure the coherence is based on
                    'clustering' - clustering coefficient
                    'closeness' - closeness centrality
                    'communicability' - communicability centrality
        :param center: 'mean' or 'median' - to use when averaging a measure over nodes
        '''
        self.selector, self.mapper = selector, resolveId(mapper)
        self.metric, self.weightFilter = metric, weightFilter
        self.center = center; self.algorithm = algorithm
        self.weighted = weighted
        IdComposer.__init__(self)
        self.__tes = TopicDocumentsScore(selector, mapper, None, mapperIsFactory)

    def __call__(self, topic):
        '''
        :param topic: (modelId, topicId)
        '''
        m = self.__tes(topic)
        W = setZeros(self.metric(m, m)) # weight matrix
        if self.weightFilter is not None:
            W = filterWeights(W, self.weightFilter)
        if self.algorithm == 'clustering':
            return self.avgClustering(W)
        elif self.algorithm == 'closeness':
            return self.avgCloseness(W)
        elif self.algorithm == 'num_connected':
            return self.numConnected(W)
        elif self.algorithm == 'communicability':
            return self.communicabilityCentrality(W)
        elif self.algorithm == 'communicability-global':
            return self.communicabilityGlobal(W)
        elif self.algorithm == 'eigen_centrality':
            return self.eigenvectorCentrality(W)
        elif self.algorithm == 'mst':
            return self.minSpanningTree(W)

    def avgClustering(self, W):
        from networkx.algorithms.cluster import clustering
        g = buildGraph(W, weighted=self.weighted)
        cl = clustering(g, weight='weight' if self.weighted else None)
        return centerMeasure(cl.values(), self.center)

    def avgCloseness(self, W):
        from networkx.algorithms.centrality import closeness_centrality
        g = buildGraph(W, weighted=self.weighted)
        cc = closeness_centrality(g, distance='weight' if self.weighted else None)
        return centerMeasure(cc.values(), self.center)

    def communicabilityCentrality(self, W):
        from networkx.algorithms.centrality import communicability_centrality as cc
        g = buildGraph(W, weighted=self.weighted)
        cl = cc(g)
        return centerMeasure(cl.values(), self.center)

    def communicabilityGlobal(self, W):
        from networkx.algorithms.centrality import communicability as c
        g = buildGraph(W, weighted=self.weighted)
        pairwiseComm = c(g)
        n = g.nodes(); N = len(n)
        comms = [ pairwiseComm[i][j]
                    for i in range(len(n))
                        for j in range(i+1, len(n)) ]
        return centerMeasure(comms, self.center)

    def eigenvectorCentrality(self, W):
        from networkx.algorithms.centrality import eigenvector_centrality_numpy as cc
        g = buildGraph(W, weighted=self.weighted)
        res = cc(g)
        return centerMeasure(res.values(), self.center)

    def numConnected(self, W):
        from networkx.algorithms.components import number_connected_components
        from math import log
        g = buildGraph(W, weighted=False)
        nc = number_connected_components(g)
        return -log(nc)

    def minSpanningTree(self, W):
        from networkx import minimum_spanning_tree
        g = buildGraph(W, weighted=True)
        mst = minimum_spanning_tree(g)
        mstw = sum(g.get_edge_data(n1, n2)['weight'] for n1, n2 in mst.edges())
        return -mstw

def centerMeasure(values, measure):
    '''
    :param values: iterable of numbers
    :param measure: 'mean' or 'median'
    '''
    if measure == 'centrality-index': return centralityGraphIndex(values)
    else:
        if measure == 'mean': return np.average(values)
        elif measure == 'median': return np.median(values)
        else: raise Exception('unsupported measure of center: %s' % measure)

def centralityGraphIndex(values):
    '''
    Calculate graph centrality index based on node centrality values.
    :param values:
    :return:
    '''
    vals = np.array(values)
    mx = vals.max()
    res = np.sum(mx - vals)
    return -res

def setZeros(W, eps=1e-10):
    '''
    Set small matrix values to zero
    :param W: ndarray
    :parameter eps: value set to 0 if its absolute value is smaller than eps
    '''
    return W * (np.abs(W) >= eps)

def filterWeights(W, interval):
    '''
    Return matrix with all weights except those inside
    give interval set to 0.
    :parameter interval: pair/list with 2 elements
    '''
    floor, ceil = interval[0], interval[1]
    return W * np.logical_and(W >= floor, W <= ceil)

def buildGraph(W, weighted=True):
    '''
    Build undirected networkx graph, from weight matrix.
    :param W: symmetric NxN matrix of edge weights
    :param weighted: if False, create unweighted graph
    :return:
    '''
    N = W.shape[0]
    g = nx.Graph()
    for n in range(N): g.add_node(n)
    for n1 in range(N):
        for n2 in range(n1+1, N):
            if W[n1, n2] != 0.0:
                if weighted: g.add_edge(n1, n2, weight=W[n1, n2])
                else: g.add_edge(n1, n2)
    return g

