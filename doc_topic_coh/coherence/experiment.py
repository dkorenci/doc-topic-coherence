import cPickle

from doc_topic_coh.coherence.tools import labelMatch
from logging_utils.setup import *
from logging_utils.tools import fullClassName
from pytopia.tools.IdComposer import IdComposer

class TopicScoringExperiment(IdComposer):
    '''
    Experiment evaluating functions for scoring topic model topics
    using roc_auc measure on a list of topics.
    '''

    def __init__(self, paramSet, scorerBuilder, ltopics, posClass, folder,
                 verbose=True, cache=False):
        '''
        :param paramSet: list-like of paramsets passed to scorerBuilder
                each 'paramset' is a dict of parameters
        :param scorerBuilder: callable building scoring functions from a paramset
        :param ltopics: list of (topic, labels) - topic is (modelId, topicId),
                labels is a string or dict of 'label':{0 or 1}
        :param posClass: string or a list of strings defining which label is positive class
        :param verbose: if true, print results during experiment runtime
        :param cache: if True, force scorerBuilder to cache function results
        '''
        self.setOfParams = paramSet
        self.scorerBuilder = scorerBuilder.__name__
        self.__builder = scorerBuilder
        self.ltopics = ltopics
        self.posClass = posClass
        IdComposer.__init__(self, class_='TSE')
        self.verbose = verbose
        self.__log = createLogger(fullClassName(self), INFO)
        self.baseFolder = folder
        self.folder = path.join(folder, self.id)
        if not path.exists(self.folder): os.mkdir(self.folder)
        self.cache = cache
        if cache:
            self.cacheFolder = path.join(self.baseFolder, 'function_cache')
            if not path.exists(self.cacheFolder): os.mkdir(self.cacheFolder)
        self.__rSetUp = False

    def __saveResults(self):
        cPickle.dump(self.resultTable, open(self.__resfile(), 'wb'))
        cPickle.dump(self.processedParams, open(self.__paramfile(), 'wb'))

    def __loadResults(self):
        self.resultTable = \
            cPickle.load(open(self.__resfile(), 'rb')) \
                if path.exists(self.__resfile()) else []
        self.processedParams = \
            cPickle.load(open(self.__paramfile(), 'rb')) \
                if path.exists(self.__paramfile()) else set()

    def __resfile(self): return path.join(self.folder, 'resultTable.pickle')
    def __paramfile(self): return path.join(self.folder, 'processedParams.pickle')

    def __msg(self, msg, level='info'):
        ''' Log message and print if self.verbose '''
        if level == 'info': self.__log.info(msg)
        elif level == 'warning': self.__log.warning(msg)
        if self.verbose:
            if level != 'warning': print msg
            else: print 'WARNING: %s' % msg

    def run(self):
        from time import time
        import gc
        gc.enable()
        self.__msg('STARTING EXPERIMENT: %s' % self.id)
        self.__loadResults()
        for p in self.setOfParams:
            pid = paramsId(p)
            print pid
            if pid in self.processedParams:
                self.__msg('params already processed: %s' % str(p))
                continue
            self.__msg('evaluating parameters: %s' % str(p))
            if self.cache:
                cp = p.copy()
                cp['cache'] = self.cacheFolder
            else: cp = p
            scorer = self.__builder(**cp)()
            t = time()
            score, classes, scores = self.__auc(scorer, self.ltopics, self.posClass, True)
            t = time()-t
            self.__msg('score %.3f , time %.3f' % (score, t))
            gc.collect()
            result = {}
            result['params'] = p.copy()
            result['scorerId'] = scorer.id
            result['roc_auc'] = score
            result['time'] = t
            result['pid'] = pid
            result['classes'] = classes
            result['scores'] = scores
            self.resultTable.append(result)
            self.processedParams.add(pid)
            self.__saveResults()

    def printResults(self, file=True, width=20):
        self.__loadResults()
        print self.id
        sr = sorted(self.resultTable, key=lambda r: -r['roc_auc'])
        if file: outf = open(self.__outfile(), mode='w')
        for i, r in enumerate(sr):
            msg = '%3d: auc: %5.3f, time: %8.3f, %s, %s, %s' % \
                  (i, r['roc_auc'], r['time'] , self.__paramSummary(r),
                    paramsId(r['params'], width, None), self.__formatParams(r['params']))
            print msg
            if file: outf.write(msg+'\n')

    def __paramSummary(self, r):
        '''
        :param r: evaluation result (a dict)
        :return:
        '''
        vecs = r['params']['vectors'] if 'vectors' in r['params'] else None
        return 'type:%18s, vectors:%12s' % (r['params']['type'], vecs)

    def __selectTopModels(self, deltaAuc=0.03, percentile=None, selectMin=10):
        '''
        Select results, ie. experimental data, for top performing models.
        Result table must be loaded.
        :return: list of selected results, selected[0] being the top performing model
        '''
        sr = sorted(self.resultTable, key=lambda r: -r['roc_auc'])
        topAuc = sr[0]['roc_auc']
        if percentile is None:
            selected = [ r for r in sr if abs(topAuc-r['roc_auc']) < deltaAuc ]
            if selectMin and len(selected) < selectMin:
                selected = sr[:1 + selectMin]
        else:
            import numpy as np
            aucs = [ r['roc_auc'] for r in sr ]
            perc = np.percentile(aucs, percentile*100)
            selected = [ r for r in sr if r['roc_auc'] >= perc ]
            print 'num. models above %.4f percentile: %d' % (perc, len(selected))
            if selectMin and len(selected) < selectMin:
                selected = sr[:selectMin]
        return selected

    def evalOnTopics(self, topics, deltaAuc=0.03, percentile=None, plotMin=10,
                     plot=False, save=True, saveDev=True):
        '''
        Eval performance of models close to the top model on a set of topics.
        :param topics: performance is evaluated on this set of topics
        :param deltaAuc: models within this distance from the top are plotted
        :param plotMin: take minimally this many top models, regardless of deltaAuc
        :return:
        '''
        from doc_topic_coh.coherence.measure_evaluation.evaluations_croelect import \
            croelectize
        # sort models by auc, select top ones
        self.__loadResults()
        sr = sorted(self.resultTable, key=lambda r: -r['roc_auc'])
        if saveDev: # save the dev results
            import pickle
            eid = 'eval_%s_%s' % (self.setOfParams.id, self.ltopics.id)
            res = [ r['roc_auc'] for r in sr ]
            print 'DEV', eid
            pickle.dump(res, open(self.__evalfile(eid), 'wb'))
        # selected[0] must be the top dev model
        selected = self.__selectTopModels(deltaAuc, percentile, plotMin)
        # evaluate models
        results = []
        print 'NUM SELECTED: %d' % len(selected)
        for i, r in enumerate(selected):
            print 'evaluating (old): ', self.__formatParams(r['params'])
            params = croelectize(r['params'])
            if self.cache:
                params['cache'] = self.cacheFolder
            print 'evaluating: ', self.__formatParams(params)
            scorer = self.__builder(**params)()
            score, classes, scores = self.__auc(scorer, topics, self.posClass, False)
            results.append(score)
        if plot:
            from matplotlib import pyplot as plt
            fig, axes = plt.subplots(1, 1)
            axes.boxplot(results)
            axes.scatter([1] * len(results), results, alpha=0.5)
            axes.plot(1, results[0], 'ro')
            plt.show()
        if save: # save result list, top model in the first position
            import pickle
            eid = 'eval_%s_%s' % (self.setOfParams.id, topics.id)
            print 'TST', eid
            pickle.dump(results, open(self.__evalfile(eid), 'wb'))

    def evalOnTopicsPrintTop(self, topics, thresh, th2per=None,
                             deltaAuc=0.03, percentile=None, selectMin=10):
        '''
        Eval performance of models close to the top model on a set of topics.
        Print selection on these evaluated models with top performance.
        :param topics: performance is evaluated on this set of topics
        :param thresh: models are printed if eval performance is above thresh
        :param deltaAuc, percentile, selectMin: pre-eval selection of top models
        :return:
        '''
        # sort models by auc, select top ones
        self.__loadResults()
        # sr = sorted(self.resultTable, key=lambda r: -r['roc_auc'])
        # selected[0] must be the top dev model
        selected = self.__selectTopModels(deltaAuc, percentile, selectMin)
        # evaluate and select models
        results = []
        for i, r in enumerate(selected):
            params = r['params']
            if self.cache:
                params['cache'] = self.cacheFolder
            scorer = self.__builder(**params)()
            score, classes, scores = self.__auc(scorer, topics, self.posClass, False)
            results.append((score, classes, score))
        import numpy as np
        if thresh == 'median':
            thresh = np.median([r[0] for r in results])
        sortSel = np.argsort([r[0] for r in results])[::-1]
        for i in sortSel:
            score, classes, scores = results[i]
            r = selected[i]
            if score >= thresh:
                params = r['params']
                devScore, evalScore = r['roc_auc'], score
                #print self.__formatParams(params)
                #print 'dev %.3f , eval %.3f' % (devScore, evalScore)
                if params['type'] == 'graph' and 'weightFilter' in params:
                    th = params['weightFilter'][1]
                    #print 'threshold percentile: ', \
                    thPerc = th2per(params['vectors'], params['distance'].__name__, th)
                    params['thresh_perc'] = thPerc
                print self.__printAsLatexRow(params, devScore, evalScore)


    def __printAsLatexRow(self, params, dev, test):
        '''
        Return params and results formatted as latex table row
        :param params: coherence measure params
        :param dev, test: AUC scores
        '''
        def lvec(params):
            vec = params['vectors']
            if vec == 'probability': return 'bag-of-words'
            elif vec == 'tf-idf': return vec
            else: # glove, glove-avg, word2vec, word2vec-avg
                dist = params['distance'].__name__ if 'distance' in params else None
                if dist == 'cosine':
                    if vec.endswith('-avg'): return vec[:-4]
                    else: return vec
                else:
                    if not vec.endswith('-avg'): return vec+'-sum'
                    else: return vec
        if params['type'] == 'graph':
            def lalgo(algo):
                if algo == 'communicability': return 'subgraph'
                else: return algo
            return \
            '\cpv{%s} & $%d$ & \cpv{%s} & $%.2f$ & \cpv{%s} & \cpv{%s} & %.3f & %.3f \\\\' % \
                (lvec(params), params['threshold'], params['distance'].__name__,
                 params['thresh_perc'], params['weighted'], lalgo(params['algorithm']),
                 dev, test
                 )
        elif params['type'] in ['avg-dist', 'variance']:
            def lagg(algo):
                if algo == 'avg-dist': return 'average'
                else: return algo
            return \
            '\cpv{%s} & $%d$ & \cpv{%s} & \cpv{%s} & %.3f & %.3f \\\\' % \
            (lvec(params), params['threshold'], params['distance'].__name__,
                lagg(params['type']), dev, test)
        elif params['type'] == 'density':
            def ldimr(dimr):
                if dimr == None: return '\cpv{None}'
                else: return '$%d$'%dimr
            def lcovar(cov):
                if cov == 'spherical': return 'scalar'
                elif cov == 'diag': return 'diagonal'
            return \
            '\cpv{%s} & $%d$ & %s & \cpv{%s} & %.3f & %.3f \\\\' % \
            (lvec(params), params['threshold'],
               ldimr(params['dimReduce']), lcovar(params['covariance']), dev, test)
        else: raise Exception('unknown coherence type: %s'%params['type'])


    def __evalfile(self, eid):
        return path.join(self.folder, '%s.pickle'%eid)

    def significance(self, scoreInd=None, N=10000, seed=8847, method ="delong"):
        '''
        Test statistical significances between top scorer and other scorers.
        :param scoreInd: indexes of scorers to compare
        :param N: number of random shuffles used to calculate significance, for bootstrap
        :return: p-value for significance
        '''
        self.__loadResults()
        res = sorted(self.resultTable, key=lambda r: -r['roc_auc'])
        if not scoreInd: scoreInd = range(0, len(res))
        rtop = res[scoreInd[0]]
        sigs = []
        for si in scoreInd[1:]:
            r = res[si]
            sig = self.__procTest(rtop['classes'], rtop['scores'], r['scores'],
                                  N, seed, method)
            sigs.append(sig)
        print 'auc top %.3f' % rtop['roc_auc'], rtop['params']
        for i, si in enumerate(scoreInd[1:]):
            r, sig = res[si], sigs[i]
            print 'auc %3d %.3f p-value: %.3f' % (si, r['roc_auc'], sig), r['params']
        # print only parameters, in format of list of dicts
        print '['
        for i, si in enumerate(scoreInd[1:]):
            r, sig = res[si], sigs[i]
            print self.__formatParams(r['params']) + ','
        print ']'

    def __formatParams(self, p):
        '''
        Format coherence measure parameters as string representing python dict,
        so that it can be usable in code without need for corrections.
        :param p: dict of 'param_name': param_value
        '''
        def modval(val):
            if hasattr(val, '__name__'): return val.__name__
            elif isinstance(val, basestring):
                return '\'%s\'' % val
            else: return str(val)
        return '{%s}'% \
               (', '.join('%s: %s'%(modval(pname), modval(pval))
                          for pname, pval in p.iteritems() if pname != 'cache' ))

    def __initR(self):
        if self.__rSetUp == True: return
        import rpy2.robjects as ro
        self.R = ro.r
        self.R('require(pROC)')
        self.R('options(warn=-1)')
        self.R('sprintf <- function(...) {}')
        self.R('deparse <- function(...) {}')
        self.__rSetUp = True

    def __procTest(self, classes, scores1, scores2, N, rseed, method = "delong"):
        from rpy2.robjects.vectors import FloatVector, IntVector
        self.__initR()
        rocTest = self.R['roc.test']
        roc = self.R['roc']
        scores1, scores2 = FloatVector(scores1), FloatVector(scores2)
        classes = IntVector(classes)
        roc1 = roc(classes, scores1)
        roc2 = roc(classes, scores2)
        params={'boot.n':N}
        paired = True
        res = rocTest(roc1, roc2, paired=paired, method=method,
                      alternative="two.sided",
                      parallel=False, **params)
        if method == "bootstrap": return float(res[7][0])
        else:
            if paired: return float(res[6][0])
            else: return float(res[7][0])

    def __outfile(self): return path.join(self.folder, 'results.txt')

    def __auc(self, scorer, ltopics, label, tolerant=False):
        '''
        Calculate area under roc curve for task of classifying topics
        using a specified topic measure.
        :param scorer: topic measure, callable mapping a topic to number
        :param ltopics: labeled topics, list of (topic, label)
        :param label: label representing the positive class
        '''
        from sklearn.metrics import roc_auc_score
        from traceback import print_exception
        import sys
        mvalues, classes = [], []
        errors = 0
        for t, tl in ltopics:
            if not tolerant:
                mv = scorer(t)
            else:
                try:
                    mv = scorer(t)
                except:
                    e = sys.exc_info()
                    if e[0] == KeyboardInterrupt: raise KeyboardInterrupt
                    self.__msg('processing of topic %s failed' % str(t), 'warning')
                    print_exception(e[0], e[1], e[2])
                    mv = None
                    errors += 1
            if mv is not None:
                mvalues.append(mv)
                classes.append(labelMatch(tl, label))
        # classes = [ for _, tl in ltopics ]
        if errors:
            self.__msg('out of %d, %d measure calculations failed' % (len(ltopics), errors))
        return roc_auc_score(classes, mvalues), classes, mvalues

def paramsId(params, width=None, header='params'):
    '''
    Converts map to hashable string uniquely identifying it.
    Keys are assumed to be strings.
    Values are transformed if they are functions or methods.
    '''
    def valueStr(obj):
        import types
        if obj == None: return None
        if hasattr(obj, 'id'):
            return obj.id
        else:
            if isinstance(obj, types.FunctionType):
                return obj.__name__
            elif isinstance(obj, types.ClassType):
                return obj.__name__
            else:
                return str(obj)
    wmod = '%s' if width is None else '%'+('%ds'%width)
    p = ','.join( wmod  % ('%s:%s' % (key, valueStr(val)))
                  for key, val in params.iteritems() )
    if header: res = '%s[%s]'%(header, p)
    else: res = p
    return res



