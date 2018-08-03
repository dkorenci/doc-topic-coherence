from pytopia.context.ContextResolver import resolveIds, resolve
from pytopia.tools.IdComposer import IdComposer
from pytopia.resource.loadSave import pickleObject
from pytopia.tools.logging import resbuild_logger

from copy import copy

@resbuild_logger
class WordDocIndexBuilder():

    def __call__(self, corpus, text2tokens, dictionary):
        ind = WordDocIndex(corpus, text2tokens, dictionary)
        ind.build()
        return ind

    def resourceId(self, corpus, text2tokens, dictionary):
        return WordDocIndex(corpus, text2tokens, dictionary).id


# requires bow_corpus_builder
# todo: is dictionary as a parameter really necessary? one could work with strings
class WordDocIndex(IdComposer):
    '''
    Index with word-document counts.
    Used as store of basic data for various tf-idf calculators.
    '''

    def __init__(self, corpus, text2tokens, dictionary):
        self.corpus, self.dictionary, self.text2tokens = \
            resolveIds(corpus, dictionary, text2tokens)
        IdComposer.__init__(self, ['corpus', 'dictionary', 'text2tokens'])

    def __eq__(self, other):
        if not isinstance(other, self.__class__): return False
        if self.id != other.id: return False
        if not self.corpus_index == other.corpus_index: return False
        if self._word2doc != other._word2doc: return False
        if self._doc2word != other._doc2word: return False
        return True

    def wordDocs(self, word):
        '''
        :param word: string or word index
        :return: list of (textId, wordCount), for all the texts where the word appears
        '''
        d = resolve(self.dictionary)
        if isinstance(word, basestring): wi = d.token2index(word)
        else: wi = word
        ci = self.corpus_index
        return [(ci[di], wc) for di, wc in self._word2doc[wi]]

    def docWords(self, docId):
        '''
        :param docId:
        :return: list of (wordIndex, wordCount), for all the words in the document
            wordIndex is the index in the WordDocIndex's dictionary
        '''
        ci = self.corpus_index
        di = ci.id2index(docId)
        return copy(self._doc2word[di])

    @property
    def corpus_index(self):
        if not hasattr(self, '_cindex'):
            cindBuild = resolve('corpus_index_builder')
            self._cindex = cindBuild(self.corpus)
        return self._cindex

    def numDocs(self): return self._numDocs

    def build(self):
        bowBuilder = resolve('bow_corpus_builder')
        bowCorpus = bowBuilder(corpus=self.corpus, text2tokens=self.text2tokens,
                               dictionary=self.dictionary)
        self._numDocs = len(bowCorpus)
        self._doc2word, self._word2doc = {}, {}
        for i, bow in enumerate(bowCorpus):
            docCnt = {}
            # add counts of the same word that might occur more than once in the bow
            for wordIndex, wordCount in bow:
                if wordIndex not in docCnt: docCnt[wordIndex] = wordCount
                else: docCnt[wordIndex] += wordCount
            # update doc-word 'matrix'
            self._doc2word[i] = []
            for wi, wc in docCnt.iteritems():
                self._doc2word[i].append((wi, wc))
                if wi in self._word2doc: self._word2doc[wi].append((i, wc))
                else: self._word2doc[wi] = [(i, wc)]

    def save(self, folder):
        if hasattr(self, '_cindex'): delattr(self, '_cindex')
        pickleObject(self, folder)

    def load(self, folder): pass

    def __getstate__(self):
        return self._word2doc, self._doc2word, self._numDocs, \
                IdComposer.__getstate__(self)

    def __setstate__(self, state):
        self._word2doc, self._doc2word, self._numDocs, idcState = state
        IdComposer.__setstate__(self, idcState)