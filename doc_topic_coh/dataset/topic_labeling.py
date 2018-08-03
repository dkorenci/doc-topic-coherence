from pytopia.context.ContextResolver import resolve
from doc_topic_coh.dataset.table_parse import TableParser
from doc_topic_coh.settings import uspol_labeled_topics
from doc_topic_coh.dataset.utils import pickleToFile, loadOrCreateResource, printLabeledTopics

gtarModelIds = [ 'uspolM0', 'uspolM1', 'uspolM2', 'uspolM10', 'uspolM11' ]

def getAllUspolTopics():
    '''
    Return all topics of us politics models as (modelId, topicId).
    '''
    return [ (mid, tid) for mid in gtarModelIds for tid in sorted(resolve(mid).topicIds()) ]

__tableParse = None
def tableParse():
    global __tableParse
    if __tableParse is None:
        from doc_topic_coh.settings import uspol_semantic_topics
        __tableParse = \
            TableParser(table=uspol_semantic_topics, themeCol='A', topicCol='B', dataRows=[(2, 134)]).parse()
    return __tableParse

def uspolTopicFeatures(topic):
    '''
    Extract features of a topic from topic - semantic topic table and topic description.
    :param topic: (modelId, topicId)
    '''
    parse = tableParse()
    mid, tid = topic
    topicLabel = '%s.%d' % (mid, tid)
    f = {}
    ptopic = parse.getTopic(topicLabel)
    # num_themes
    f['num_themes'] = len(ptopic.themes)
    # table_mixed
    f['table_mixed'] = ptopic.mixed
    model = resolve(mid)
    l = str(model.description.topic[tid].label).lower().strip()
    # label_mixed
    if l.startswith('mix:') or l.startswith('mixture:'): f['label_mixed'] = True
    else: f['label_mixed'] = False
    # label_mixonly
    if l == 'mix' or l == 'mixture': f['label_mixonly'] = True
    else: f['label_mixonly'] = False
    # label_noise
    if l.endswith('et al'): f['label_noise'] = True
    else: f['label_noise'] = False
    # stopwords
    f['stopwords'] = (l == 'stopwords')
    return f

def uspolFeatures2Labels(f, format='string'):
    '''
    Label us politics topics as one of these mutually exclusive categories:
    theme, theme_noise, theme_mix, theme_mix_noise, noise
    :param f: topic features
    :param format: map or string
    '''
    numThemes = f['num_themes']
    c = {}
    if numThemes == 1:
        if f['table_mixed'] | f['label_mixed'] | f['label_noise']:
            c['theme_noise'] = 1
        else: c['theme'] = 1
    elif numThemes == 0: c['noise'] = 1
    elif numThemes > 1:
        if f['label_noise']:
            c['theme_mix_noise'] = 1
        else: c['theme_mix'] = 1
    else: raise Exception('illegal number of themes: %s' % str(numThemes))
    if format == 'string':
        for l, v in c.iteritems():
            if v == 1: return l
        return None
    return c

def labelAllUspolTopics(feats2cat=uspolFeatures2Labels):
    '''
    Label all the us politics topics.
    :param feats2cat: callable that accepts a feature map
            and creates category map
    :return: list of (topic, categories)
    '''
    from doc_topic_coh.resources import pytopia_context
    from doc_topic_coh.coherence.tools import IdList
    topics = [(t, feats2cat(uspolTopicFeatures(t))) for t in getAllUspolTopics()]
    topics = IdList(topics)
    topics.id = 'uspol_topics_categorized'
    return topics

def uspolTopicsLabeled(create=False):
    '''
    Load set of all labeled us politics topics from file, if able, or create it.
    '''
    return loadOrCreateResource(labelAllUspolTopics, uspol_labeled_topics, create)

def uspolTopicsLabeledSave():
    from doc_topic_coh.resources import pytopia_context
    topics = uspolTopicsLabeled(True)
    pickleToFile(topics, uspol_labeled_topics)

def printStats():
    from doc_topic_coh.dataset.utils import topicLabelStats
    topicLabelStats(uspolTopicsLabeled())

if __name__ == '__main__':
    #uspolTopicsLabeledSave()
    print labelAllUspolTopics()
    #printStats()
    #printLabeledTopics(uspolTopicsLabeled())