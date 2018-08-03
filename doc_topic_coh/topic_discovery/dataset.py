from doc_topic_coh.dataset.topic_splits import uspolTopicsLabeled
from doc_topic_coh.dataset.topic_labeling import tableParse

def topicThemes(topic, label, emptyMixed=False):
    '''
    :param topic: (modelId, topicId)
    :param emptyMixed: if True, topics labeled as mixed will have no themes
    :return: list of themes (semantic topics) associated with the topic
    '''
    if emptyMixed and label in ['theme_mix', 'theme_mix_noise']: return []
    parse = tableParse()
    topicLabel = '%s.%d' % topic
    ptopic = parse.getTopic(topicLabel)
    th = [ lab for lab, th in ptopic.themes.iteritems() ]
    return th

def selectTopics(topics, filterByLabel=None):
    '''
    :param topics: list of (topic, label)
    :param filterByLabel: list of string labels
    :return: list of topics labeled with one of the labels, or all topics if it is None
    '''
    if not filterByLabel: return topics
    return [(t, l) for t, l in topics if l in filterByLabel]

def allTopicsNoMix():
    topics = selectTopics(uspolTopicsLabeled(), ['theme', 'theme_noise', 'noise'])
    return [ (t, topicThemes(t, l)) for t, l in topics ]

def allTopicsMixedEmpty():
    return [(t, topicThemes(t, l, emptyMixed=True)) for t, l in uspolTopicsLabeled()]

if __name__ == '__main__':
    print allTopicsNoMix()