'''
Functionality for extracting statistics about corpus' document vectors pairwise distances.
'''

import doc_topic_coh.resources.pytopia_context
from pytopia.context.ContextResolver import resolve

from pytopia.measure.topic_distance import cosine, l1, l2, l2squared, lInf, canberra
import numpy as np
from os.path import join

def tfidf(corpus='us_politics', text2tokens='RsssuckerTxt2Tokens', dict='us_politics_dict'):
    builder = resolve('corpus_tfidf_builder')
    return builder(corpus=corpus, dictionary=dict, text2tokens=text2tokens)

def wordprob(corpus='us_politics', text2tokens='RsssuckerTxt2Tokens', dict='us_politics_dict'):
    from pytopia.resource.text_prob_vector.TextProbVectorizer import TextProbVectorizer
    vectorizer = TextProbVectorizer(text2tokens=text2tokens, dictionary=dict)
    textVectors = resolve('corpus_text_vectors_builder')(vectorizer=vectorizer, corpus=corpus)
    return textVectors

def worldvec(type='word2vec', corpus='us_politics'):
    from pytopia.resource.word_vec_aggregator.WordVecAggregator import WordVecAggregator
    if type.startswith('word2vec'):
        w2vec = resolve('word2vec_builder')('GoogleNews-vectors-negative300.bin')
    else:
        w2vec = resolve('glove_vectors_builder')('glove.6B.300d.txt')
    avg = True if type.endswith('avg') else None
    text2vec = WordVecAggregator('alphanum_gtar_stopword_tokenizer', w2vec, None, avg)
    mapper = resolve('corpus_text_vectors_builder')(vectorizer=text2vec, corpus=corpus)
    return mapper

def worldvecCro(type='word2vec', corpus='iter0_cronews_final'):
    from pytopia.resource.word_vec_aggregator.WordVecAggregator import WordVecAggregator
    if type.startswith('word2vec'):
        w2vec = resolve('word2vec_builder')('word2vec.hrwac.cbow.vectors.bin')
    else:
        w2vec = resolve('glove_vectors_builder')('glove.hrwac.300d.txt')
    avg = True if type.endswith('avg') else None
    text2vec = WordVecAggregator('croelect_alphanum_stopword_tokenizer', w2vec, None, avg)
    mapper = resolve('corpus_text_vectors_builder')(vectorizer=text2vec, corpus=corpus)
    return mapper

def docuDistStats(vectorizers, distances, corpus='us_politics', sampleSize=100000, rndSeed=54778,
                  savePath='.', models = None):
    '''
    :param corpus:
    :param vectorizer:
    :param distance:
    :param sampleSize:
    :return:
    '''
    from numpy import triu_indices
    from numpy.random import choice, seed
    corpus = resolve(corpus)
    ids, id2txt = [], {}
    for txto in corpus:
        ids.append(txto.id)
        id2txt[txto.id] = txto
    N = len(ids)
    print 'corpus indexed, size %d' % N
    # sample pairs of ids
    pairs = triu_indices(N, 1)
    numPairs = len(pairs[0])
    print 'pairs array created'
    seed(rndSeed)
    indSample = choice(numPairs, sampleSize, replace=False)
    print 'sampling'
    idPairs = [ (ids[pairs[0][i]], ids[pairs[1][i]]) for i in indSample ]
    pairs = None
    import gc
    gc.collect()
    # create pair distances
    print 'calculating distances'
    if not isinstance(distances, list): distances = [distances]
    if not isinstance(vectorizers, list): vectorizers = [vectorizers]
    mlabel = '' if models is None else '_'.join(m for m in models)
    for vectorizer in vectorizers:
        vectors = {}
        for distance in distances:
            fname = 'vectorizer[%s]_distance[%s]_models[%s]_stats' % \
                    (vectorizer.id, distance.__name__, mlabel)
            dists = np.empty(len(idPairs), dtype=np.float64)
            print fname
            for i, p in enumerate(idPairs):
                id1, id2 = p
                if not models:
                    if id1 not in vectors: vectors[id1] = vectorizer(id1)
                    if id2 not in vectors: vectors[id2] = vectorizer(id2)
                    dists[i] = distance(vectors[id1], vectors[id2])
                else:
                    for m in models:
                        vectors[id1] = vectorizer(id1, m)
                        vectors[id2] = vectorizer(id2, m)
                        dists[i] = distance(vectors[id1], vectors[id2])
                #if i % 10000 == 0: print '  %d distances calculated' % i
            statistics(dists, join(savePath, fname))

def statistics(vals, saveFile):
    from matplotlib import pyplot as plt
    from stat_utils.utils import Stats
    from numpy import percentile
    percs = np.arange(0.05, 1.0, 0.05)
    percs = np.insert(percs, 0, np.arange(0.01, 0.05, 0.01))
    percVals = percentile(vals, percs*100, interpolation='higher')
    f = open(saveFile+'.txt', 'w')
    f.write(str(Stats(vals))+'\n')
    # print values of grid search percentiles separately
    threshPercs = [0.02, 0.05, 0.1, 0.25, 0.5, 0.75]
    f.write('[')
    for i in range(len(percs)):
        if np.isclose(percs[i], threshPercs).sum():
            f.write(('%.5f' % percVals[i])+', ')
    f.write(']\n')
    # print all percentiles and values
    for i in range(len(percs)):
        s = '%.2f, %.5f' % (percs[i], percVals[i])
        f.write(s+'\n')
    # plot
    fig, axes = plt.subplots(3)
    axes[0].boxplot(vals)
    axes[1].hist(vals, bins=100, normed=True)
    # percentile barchart
    x = np.arange(len(percs))+0.5
    axes[2].bar(x-0.5, percVals, color='gray', width=0.5)
    axes[2].set_xticks(x-0.25)
    axes[2].set_xticklabels(['%.2f'%p for p in percs])
    #plt.draw()
    if saveFile:
        plt.savefig(saveFile+'.pdf')
    #plt.show()

def runAll(sample=100000):
    savePath = '/datafast/doc_topic_coh/distance_distribution/'
    distances = [cosine, l1, l2]
    # uspolitics CNT
    #docuDistStats([wordprob(), tfidf()], distances = distances, sampleSize=sample, savePath=savePath)
    # # uspolitics EMBD
    #docuDistStats(worldvec('glove-avg'), distances=[l1, l2], sampleSize=sample, savePath=savePath)
    #docuDistStats(worldvec('glove'), distances=distances, sampleSize=sample, savePath=savePath)
    # docuDistStats(worldvec('word2vec-avg'), distances=[l1, l2], sampleSize=sample, savePath=savePath)
    # docuDistStats(worldvec('word2vec'), distances=distances, sampleSize=sample, savePath=savePath)
    # # croelect CNT
    # docuDistStats([wordprob(corpus='iter0_cronews_final', dict='croelect_dict_iter0',
    #                         text2tokens='CroelectTxt2Tokens'),
    #                tfidf(corpus='iter0_cronews_final', dict='croelect_dict_iter0',
    #                         text2tokens='CroelectTxt2Tokens')],
    #                 corpus='iter0_cronews_final',
    #                 distances=distances, sampleSize=sample, savePath=savePath)
    # # croelect EMBD
    # docuDistStats(worldvecCro('glove-avg'), distances=[l1, l2], corpus='iter0_cronews_final',
    #               sampleSize=sample, savePath=savePath)
    # docuDistStats(worldvecCro('glove'), distances=distances, corpus='iter0_cronews_final',
    #               sampleSize=sample, savePath=savePath)
    docuDistStats(worldvecCro('word2vec-avg'), distances=[l1, l2], corpus='iter0_cronews_final',
                  sampleSize=sample, savePath=savePath)
    docuDistStats(worldvecCro('word2vec'), distances=distances, corpus='iter0_cronews_final',
                  sampleSize=sample, savePath=savePath)

if __name__ == '__main__':
    runAll(1000)