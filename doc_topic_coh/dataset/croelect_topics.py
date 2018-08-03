# -*- coding: utf-8 -*-

from doc_topic_coh.resources import pytopia_context

from doc_topic_coh.dataset.table_parse import TableParser
from pytopia.context.ContextResolver import resolve

from doc_topic_coh.dataset.utils import topicLabelStats, printLabeledTopics
from doc_topic_coh.coherence.tools import IdList

from doc_topic_coh.settings import croelect_semantic_topics

__tableParse = None
def croelectTableParse():
    global __tableParse
    if __tableParse is None:
        __tableParse = \
            TableParser(table=croelect_semantic_topics, dataRows=[(2, 96)],
                        themeCol='A', topicCol='B').parse()
    return __tableParse

def croelectTopicFeatures(topic, table=None):
    '''
    Extract features of a topic from topic - semantic topic table and topic description.
    :param topic: (modelId, topicId)
    '''
    mid, tid = topic
    model = resolve(mid)
    assert mid.startswith('croelect_')
    mid = mid[9:]
    parse = croelectTableParse()
    topicLabel = '%s.%d' % (mid, tid)

    #print topicLabel
    f = {}
    ptopic = parse.getTopic(topicLabel)
    #print ptopic.themes
    # num_themes
    f['num_themes'] = len(ptopic.themes)
    # table_mixed
    f['table_mixed'] = ptopic.mixed
    l = unicode(model.description.topic[tid].label).lower().strip()
    # label_noiseonly
    if l == u'šum': f['label_noiseonly'] = True
    else: f['label_noiseonly'] = False
    # label_noise
    if  u'šum' in l: f['label_noise'] = True
    else: f['label_noise'] = False
    return f

def croelectFeatures2Labels(f, format='string'):
    '''
    Label croelect topics as one of these mutually exclusive categories:
    theme, theme_noise, theme_mix, theme_mix_noise, noise
    :param f: topic feature map
    :param format: map or string
    '''
    numThemes = f['num_themes']
    c = {}
    if numThemes == 1:
        if f['label_noise']: c['theme_noise'] = 1
        else: c['theme'] = 1
    elif numThemes == 0: c['noise'] = 1
    elif numThemes > 1:
        if f['label_noise']:
            c['theme_mix_noise'] = 1
        else: c['theme_mix'] = 1
    else: raise Exception('illegal number of themes: %s' % str(numThemes))
    if f['label_noiseonly']: c = {'noise':1}
    if format == 'string':
        for l, v in c.iteritems():
            if v == 1: return l
        return None
    return c

croelectModelIds = ['croelect_model1', 'croelect_model2', 'croelect_model3', 'croelect_model4']
def getAllCroelectTopics():
    '''
    Return all topics of croelect models as (modelId, topicId).
    '''
    all = [ (mid, tid) for mid in croelectModelIds for tid in sorted(resolve(mid).topicIds()) ]
    return all

def labelAllCroelectTopics():
    topics = [(t, croelectFeatures2Labels(croelectTopicFeatures(t)))
              for t in getAllCroelectTopics()]
    topics = IdList(topics)
    topics.id = 'croelect_topics_categorized'
    return topics

from doc_topic_coh.settings import croelect_labeled_topics
from doc_topic_coh.dataset.utils import pickleToFile, loadOrCreateResource

def croelectTopicsLabeled(create=False):
    '''
    Load set of all croelect topics from file or create it.
    '''
    return loadOrCreateResource(labelAllCroelectTopics, croelect_labeled_topics, create)

def croelectTopicsLabeledSave():
    from doc_topic_coh.resources import pytopia_context
    topics = croelectTopicsLabeled(True)
    pickleToFile(topics, croelect_labeled_topics)

def printTopicStats():
    alltopics = croelectTopicsLabeled()
    topicLabelStats(alltopics)

if __name__ == '__main__':
    #croelectTopicsLabeledSave()
    #printTopicStats()
    print labelAllCroelectTopics()
    #printLabeledTopics(croelectTopicsLabeled())