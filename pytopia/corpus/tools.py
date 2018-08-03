from pytopia.context.ContextResolver import resolve
from scipy.sparse import dok_matrix
import numpy as np

def bowCorpus2Matrix(corpus, dict, sparse=True, dtype=np.uint32):
    '''
    Create matrix from bow corpus.
    Rows are indices of documents in the corpus, columns are dictionary
    indices of words words, values are number of words in the document.
    :param corpus: list-like of docs where each doc is list of (wordIndex, wordCount)
    :param sparse: weather to return scipy.sparse matrix of np.ndarray
    '''
    rows, cols = len(corpus), dict.maxIndex() + 1
    if sparse: matrix = dok_matrix((rows, cols), dtype=dtype)
    else: matrix = np.zeros((rows, cols), dtype=dtype)
    for i, bow in enumerate(corpus):
        matrix[i] = bow2Vector(bow, cols, sparse=sparse)
    return matrix

def bow2Vector(bow, vectorDim, type=np.uint32, sparse=False):
    '''
    Transforms bow, list-like of (word index, word count)
    to scipy sparse vector or ndarray
    :param type: dtype large enough to hold counts
    '''
    if sparse:
        v = dok_matrix((1, vectorDim), dtype=type)
        for i, cnt in bow: v[0, i] = cnt
    else:
        v = np.zeros(vectorDim, dtype=type)
        for i, cnt in bow: v[i] = cnt
    return v