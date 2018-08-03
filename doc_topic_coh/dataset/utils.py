import pickle
from os import path

def topicLabelStats(ltopics):
    '''
    Display topic label distribution
    :param ltopics: list of (topic, label)
    :return:
    '''
    lcnt = {}; N = len(ltopics)
    for _, labeling in ltopics:
        if isinstance(labeling, dict):
            labels = [ l for l, v in labeling.iteritems() if v == 1 ]
        else: labels = [labeling]
        for lab in labels:
            if lab in lcnt: lcnt[lab] += 1
            else: lcnt[lab] = 1
    print 'number of topics:', N
    for l in sorted(lcnt.keys()):
        print l, '%.4f'%(float(lcnt[l])/N), '%4d'%lcnt[l]

def topicTabLabel(t):
    '''
    Convert pytopia (mid, tid) topic to label used in annotation excel tables
    '''
    return '%s.%d'%(t[0][9:],t[1])

def pickleToFile(obj, fname):
    pickle.dump(obj, open(fname, 'wb'))

def unpickleFromFile(fname):
    import traceback
    if path.exists(fname):
        try:
            res = pickle.load(open(fname, 'rb'))
            return res
        except:
            print 'unpickling failed: ', fname
            #print(traceback.format_exc())
            return None
    else: return None

def loadOrCreateResource(createMethod, fname, create=False):
    '''
    Load resource from file or create it if loading fails or if create == True.
    '''
    if not create:
        res = unpickleFromFile(fname)
        if res is not None:
            print 'loaded', fname
            return res
        else:
            print 'loading failed', fname
    print 'creating', fname
    return createMethod()

def printLabeledTopics(ltopics):
    if hasattr(ltopics, 'id'): print 'Topic set id: %s' % ltopics.id
    else: print 'Topic set'
    for t, l in ltopics:
        print 'topic: %s.%s , label: %s'%(t[0], t[1], l)

def printTopicSplit(split):
    lt1, lt2 = split
    printLabeledTopics(lt1)
    printLabeledTopics(lt2)
