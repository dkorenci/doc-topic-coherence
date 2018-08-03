from pytopia.context.ContextResolver import resolve

class AggregateThemeCount():
    '''
    Counts themes covered by a list of topic annotated with themes.
    Repeated topics are not counted.
    '''

    def __init__(self, eqtop, verbose=False):
        '''
        :param eqtop: callable accepting two topics and returning
          true if they are considered equal.
        '''
        self.eqtop = eqtop
        self.verbose = verbose

    def __call__(self, ttopics):
        '''
        :param ttopics: list of (topic, list of themes)
        :return: list l[N] = cumulative. num themes @ topics[:N],
                    not counting repeated topics.
        '''
        cthemes = set()
        cumul = []
        topics = []
        for t, themes in ttopics:
            topicRepeated = False
            for pt, pth in topics:
                if self.eqtop(pt, t):
                    topicRepeated = True
                    if self.verbose:
                        if pth != themes:
                            print 'theme mismatch'
                            print 'new topic:', t, themes
                            print 'old topic: ', pt, pth
                    break
            if not topicRepeated:
                if len(themes) > 0:
                    topics.append((t, themes))
                # if self.verbose:
                #     print 'topic accepted:', t, themes
                for th in themes: cthemes.add(th)
                cumul.append(len(cthemes))
        if self.verbose: print 'TOTAL THEMES: ', len(cthemes)
        return cumul

def topvec(t):
    ''' Fethc topic vector for a topic specified by (modelId, topicId) '''
    mid, tid = t
    return resolve(mid).topicVector(tid)

class TopicDistEquality():
    '''
    Asses topic equality via distance function defined on topics.
    '''
    def __init__(self, dist, th):
        self.dist, self.threshold = dist, th

    def __call__(self, t1, t2):
        v1, v2 = topvec(t1), topvec(t2)
        return self.dist(v1, v2) <= self.threshold

def themeCount(ttopics):
    '''
    :param ttopics: list of (topic, list of themes)
    :return: list l[N] = cumulative. num themes @ topics[:N]
    '''
    cthemes = set()
    cumul = []
    for _, themes in ttopics:
        for th in themes: cthemes.add(th)
        cumul.append(len(cthemes))
    return cumul

def sortByCoherence(ttopics, coh, printSorted=False):
    '''
    :param ttopics: list of (topic, list of themes)
    :param coh: topic coherence measure
    :param desc: if True, sort descending
    :return:
    '''
    topCoh = { t: coh(t) for t, _ in ttopics}
    keyFunc = lambda tt: topCoh[tt[0]]
    res = sorted(ttopics, key=keyFunc, reverse=True)
    if printSorted:
        for t, th in res:
            print t, th
            print topCoh[t]
    return res

def plotThemeCounts(cohCounts, rndCounts, maxx=None,
                    palette=['b', 'k', 'g', 'y', 'c', 'm'],
                    labels=['graph1', 'graph2', 'baseline', 'word coherence']):
    from matplotlib import pyplot as plt
    import numpy as np
    fig, axes = plt.subplots(1,2)
    maxlen = max(max(len(l) for l in cohCounts), max(len(l) for l in rndCounts))
    # extend list to same length
    for cnt in cohCounts: cnt.extend([cnt[-1]] * (maxlen - len(cnt)))
    for cnt in rndCounts: cnt.extend([cnt[-1]] * (maxlen - len(cnt)))
    # aggregates of random counts
    rnda = np.array(rndCounts)
    rndAvg = np.average(rnda, 0)
    rndMax = np.max(rnda, 0)
    rndMin = np.min(rnda, 0)
    # print the number of topics for each measure
    for i in range(maxlen):
        print i
        print 'coherences'
        for c in cohCounts:
            print '     ', c[i]
        print 'random'
        print '     ',rndAvg[i]
    #palette = 'bgkcmyb'
    x = range(maxlen)
    axes[0].set_ylim([0, 100])
    if maxx: axes[0].set_xlim([0, maxx])
    for i, cnt in enumerate(cohCounts):
        axes[0].plot(x, cnt, color=palette[i], label=labels[i])
    axes[0].plot(x, rndAvg, color='r', label='random avg.')
    axes[0].plot(x, rndMax,  ':', color='r', label='random max')
    axes[0].plot(x, rndMin,  ':', color='r', label='random min')
    handles, labs = axes[0].get_legend_handles_labels()
    axes[0].legend(handles, labs, loc='upper left', prop={'size': 18})
    axes[0].yaxis.grid(True)
    axes[0].xaxis.grid(True)
    # plot difference between coherences and average random
    axes[1].set_ylim([-10, 25])
    if maxx: axes[1].set_xlim([0, maxx])
    for i, cnt in enumerate(cohCounts):
        axes[1].plot(x, cnt-rndAvg, color=palette[i], label=labels[i])
    handles, labs = axes[1].get_legend_handles_labels()
    axes[1].legend(handles, labs, loc='upper left', prop={'size': 18})
    axes[1].yaxis.grid(True)
    axes[1].xaxis.grid(True)
    plt.tight_layout(pad=0)
    plt.show()