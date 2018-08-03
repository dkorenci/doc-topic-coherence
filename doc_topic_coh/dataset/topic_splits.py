from sklearn.model_selection import train_test_split

from doc_topic_coh.coherence.tools import IdList
from doc_topic_coh.resources import pytopia_context
from doc_topic_coh.dataset.topic_labeling import uspolTopicsLabeled
from doc_topic_coh.dataset.utils import loadOrCreateResource
from doc_topic_coh.settings import dev_test_split

def devTestSplit(create=False):
    return loadOrCreateResource(topicSplit, dev_test_split, create)

def topicSplit():
    ltopics = uspolTopicsLabeled()
    topics, labels = [ t for t, _ in ltopics ], [ l for _, l in ltopics ]
    split = train_test_split(ltopics, train_size=120,
                             stratify=labels, random_state=9984)
    dev = IdList(split[0]); dev.id = 'dev_%s' % ltopics.id
    test = IdList(split[1]); test.id = 'test_%s' % ltopics.id
    return dev, test

def saveDevTestSplit():
    from doc_topic_coh.dataset.utils import pickleToFile
    split = devTestSplit(True)
    pickleToFile(split, dev_test_split)

if __name__ == '__main__':
    #saveDevTestSplit()
    devTestSplit()

