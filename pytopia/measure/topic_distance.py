'''
Distance metrics between two topics.
Each metric is a callable implementing a function
f(m1, m2) -> double, where m1 and m2 are either arrays of the same length,
or matrices with same number of columns, in which case batch computation
will be performed if possible and a row x row distance matrix returned.
'''

from scipy.spatial.distance import cosine as cosineSp, minkowski, cdist, \
    euclidean, sqeuclidean, chebyshev, canberra as canberraSp
import numpy as np

def apply2RowPairs(m1, m2, f):
    '''
    Apply function that operates on numpy vectors to all pairs
    of rows of two matrices (with the same number of columns).
    :return: matrix of function values, with dim. rows(m1) x rows(m2)
    '''
    assert m1.shape[1] == m2.shape[1]
    R1, R2 = m1.shape[0], m2.shape[0]
    r = np.empty((R1, R2))
    for i in range(R1):
        for j in range(R2):
            r[i,j]=f(m1[i,:],m2[j,:])
    return r

def kullbackLeibler(t1, t2):
    '''
    :param t1, t2: ndarray representing probability distribution
    :return:
    '''
    return (t1*np.log(t1/t2)).sum()

def jensenShannon(m1, m2):
    if len(m1.shape) == 1:
        avg = (m1+m2)*0.5
        return 0.5*(kullbackLeibler(m1, avg)+kullbackLeibler(m2, avg))
    else:
        return apply2RowPairs(m1, m2, jensenShannon)

def cosine(m1, m2):
    if len(m1.shape) == 1: return cosineSp(m1, m2)
    else: return cdist(m1, m2, 'cosine')

def l1(m1, m2):
    if len(m1.shape) == 1: return minkowski(m1, m2, 1)
    else: return cdist(m1, m2, 'minkowski', p=1)

def l2(m1, m2):
    if len(m1.shape) == 1: return euclidean(m1, m2)
    else: return cdist(m1, m2, 'euclidean')

def l2squared(m1, m2):
    if len(m1.shape) == 1: return sqeuclidean(m1, m2)
    else: return cdist(m1, m2, 'sqeuclidean')

def lInf(m1, m2):
    if len(m1.shape) == 1: return chebyshev(m1, m2)
    else: return cdist(m1, m2, 'chebyshev')

def canberra(m1, m2):
    if len(m1.shape) == 1:
        vecSize = len(m1)
        return canberraSp(m1, m2) / vecSize
    else:
        vecSize = m1.shape[1]
        return cdist(m1, m2, 'canberra') / vecSize

def batchDistance(m1, m2, metric, **params):
    '''Calculate distances between rows of two matrices.'''
    res = cdist(m1, m2, metric=metric, **params)
    return res

def rescaledDot(t1, t2):
    t1desc = np.sort(t1)[::-1]
    t2asc = np.sort(t2)
    t2desc = t2asc[::-1]
    dot = np.dot(t1,t2)
    mn = np.dot(t1desc,t2asc)
    mx = np.dot(t1desc,t2desc)
    return 1-(dot-mn)/(mx-mn)
