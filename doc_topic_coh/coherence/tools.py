def labelMatch(tlabel, label):
    '''
    Return 1 or 0 designating weather topic labeling matches
     any of the string labels, or not
    :param tlabel: either a string or a map: string -> {0, 1}
    :param label: a string or a list of strings
    :return:
    '''
    labels = label if isinstance(label, list) else [label]
    labelset = set(labels)
    if isinstance(tlabel, basestring):
        return 1 if tlabel in labelset else 0
    elif isinstance(tlabel, dict):
        for l in labels:
            if tlabel[l] == 1: return 1
        return 0
    else: raise Exception('illegal topic label')

def labelsMatch(ltopics, label):
    '''
    Return array of 0s and 1s, each value corresponding to a topic label matching the label.
    :param ltopics: labeled topics, list of (topic, label)
    :param label: a string or a list of strings
    :return:
    '''
    return [ labelMatch(tl, label) for _, tl in ltopics ]

def flattenParams(params={}):
    '''
    :param params: map key -> value or a list of values
    :return: list of maps each representing one of the possible combinations
             where each key has only one possible value assigned to it
    '''
    keys = params.keys(); NK = len(keys)
    res = []; cm = {}
    def fillMapRecursive(ki):
        if ki == NK:
            res.append(cm.copy())
            return
        key = keys[ki]
        val = params[key]
        if not isinstance(val, list):
            cm[key] = val
            fillMapRecursive(ki+1)
        else:
            for v in val:
                cm[key] = v
                fillMapRecursive(ki + 1)
    fillMapRecursive(0)
    return res

def testFlatten():
    fl = flattenParams({'k1':['v1.1','v1.2'], 'k2':'v2', 'k3':['v3.1','v3.2','v3.3']})
    for p in fl: print p

def joinParams(pl1, pl2):
    '''
    :param p1, pl2: list of maps
    :return: list of maps, each being 'sum' of m1 \in p1, m2 \in p2,
            for all combinations
    '''
    res = []
    {}.update()
    for p1 in pl1:
        for p2 in pl2:
            np = p1.copy(); np.update(p2)
            res.append(np)
    return res

def auc_alternative(classes, ranks):
    posi = [ i for i, c in enumerate(classes) if c == 1 ]
    negi = [ i for i, c in enumerate(classes) if c == 0 ]
    posNeg = [ (pi, ni) for pi in posi for ni in negi ]
    N = float(len(posNeg))
    matched = sum(1.0 for pi, ni in posNeg if ranks[pi] > ranks[ni])
    return matched / N

def testJoin():
    pl1 = [ {'a':1}, {'a':2} ]
    pl2 = [ {'b':1}, {'b':2} ]
    for p in joinParams(pl1, pl2): print p

if __name__ == '__main__':
    testJoin()


class IdList(list): pass


class IdDict(dict): pass