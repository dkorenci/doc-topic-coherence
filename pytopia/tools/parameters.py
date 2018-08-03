'''
Tools for working with parameter sets, ie. key -> value maps.
'''

# Classes that enable properties, such as id, to be assigned to lists and dicts
class IdList(list): pass
class IdDict(dict): pass

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

def testJoin():
    pl1 = [ {'a':1}, {'a':2} ]
    pl2 = [ {'b':1}, {'b':2} ]
    for p in joinParams(pl1, pl2): print p

if __name__ == '__main__':
    testFlatten()