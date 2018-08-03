from pytopia.context.ContextResolver import resolve
from pytopia.tools.IdComposer import IdComposer

class TopDocSelector(IdComposer):
    '''
    Select either top-K documents or documents with topic-weights above the threshold.
    '''

    def __init__(self, threshold):
        '''
        :param threshold: integer (for top K selction),
            a number between 0 and 1 (as topic-weight threshold)
            or 'above-random' that sats topic-weight threshold to 1/num_topics
        '''
        self.threshold = threshold2str(threshold)
        IdComposer.__init__(self)
        self.__threshold = threshold

    # requires: corpus_topic_index_builder
    def __call__(self, topic):
        '''
        :param topic: (modelId, topicId)
        :return:
        '''
        mid, tid = topic
        model = resolve(mid)
        ctiBuilder = resolve('corpus_topic_index_builder')
        cti = ctiBuilder(corpus=model.corpus, model=model)
        topicTexts = cti.topicTexts(tid)
        if self.__threshold == 'above-random':
            rnd = 1.0 / model.numTopics()
            texts = [textId for textId, w in topicTexts if w > rnd]
        elif 0.0 < self.__threshold < 1.0:
            texts = [textId for textId, w in topicTexts if w > self.__threshold]
        elif isinstance(self.__threshold, (int, long)) :
            texts = [textId for textId, _ in topicTexts[:self.__threshold]]
        return texts

def threshold2str(t):
    if isinstance(t, float): return '%.3f' % t
    else: return str(t)
