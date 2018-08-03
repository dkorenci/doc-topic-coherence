import numpy as np

from pytopia.context.ContextResolver import resolve

# requires: corpus_topic_index_builder
# requires: corpus_tfidf_builder
def tfIdfMatrix(t, threshold=0.1):
    '''
    Create matrix where rows are tf-idf vectors of top documents for the topic
    :param t: (modelId, topicId), where modelId is in context
    :param threshold: use only documents with topic weight above treshold
    :return matrix of tfidf vectors, as ndarray
    '''
    mid, tid = t
    model = resolve(mid)
    ctiBuilder = resolve('corpus_topic_index_builder')
    cti = ctiBuilder(corpus=model.corpus, model=model)
    topicTexts = cti.topicTexts(tid)
    if 0.0 < threshold < 1.0:
        texts = [textId for textId, w in topicTexts if w > threshold]
    else: texts = [textId for textId, w in topicTexts[:threshold]]
    tfidfBuilder = resolve('corpus_tfidf_builder')
    tfidf = tfidfBuilder(corpus=model.corpus, dictionary=model.dictionary,
                         text2tokens=model.text2tokens)
    vecs = [ np.array(tfidf[txtid]) for txtid in texts ]
    return np.array(vecs)