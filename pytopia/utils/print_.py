import numpy as np

def topTopicWords(topic, dict, topWords = 10):
    '''
    Return a string of top words representing a topic.
    :param topic: scipy vector of word (integer indexes) weights
    :param dict: pytopia dictionary
    :param topWords: number of top words to include
    '''
    top_indices = topVectorIndices(topic, topWords)
    words = [dict.index2token(i) for i in top_indices]
    return words

def topTopicWordsString(topic, dict, topWords = 10):
    return u' '.join(topTopicWords(topic, dict, topWords))

def topWordsAndWeights(topic, dict, topWords = 10):
    '''
    Return, as separate lists, weights and words corresponding to top-weighted words.
    :param topic: scipy vector of word (integer indexes) weights
    :param dict: word index -> word string mapping
    :param topWords: number of top words to include
    '''
    ti = topVectorIndices(topic, topWords)
    return [dict[i] for i in ti], [topic[i] for i in ti]

def topVectorIndices(vec, topN):
    '''
    Indices of vector values with largest values.
    :param vec: scipy vector
    '''
    # get indices in sorted order, reverse, take first topWords
    if len(vec) < topN: topN = len(vec)
    return np.argsort(vec)[::-1][:topN]

