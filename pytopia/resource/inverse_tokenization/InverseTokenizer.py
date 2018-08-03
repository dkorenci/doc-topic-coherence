from pytopia.tools.IdComposer import IdComposer
from pytopia.context.ContextResolver import resolve, resolveIds
from pytopia.resource.loadSave import pickleObject

#todo write tests
class InverseTokenizer(IdComposer):
    '''
    Data and interface for mapping processed (lemmatized, stemmed, ...) tokens
    back to original words from text.
    '''

    def __init__(self, corpus, text2tokens, lowercase):
        self.corpus, self.text2tokens = resolveIds(corpus, text2tokens)
        self.lowercase = lowercase
        IdComposer.__init__(self)

    def __initDataStructures(self):
        self.token2words = {} # { token -> {word -> freq} }
        self.topFreq = {} # token -> freq. of most frequent word
        self.topWord = {} # token -> most frequent word

    def __call__(self, token):
        ''' Return word with highest frequency for the token. '''
        if token in self.topWord: return self.topWord[token]
        else: return None

    def allWords(self, token):
        ''' Return all words corresponding to token, sorted descending by frequency. '''
        if token in self.token2words:
            wordFreq = [wf for wf in self.token2words[token].iteritems()]
            wordFreq.sort(key=lambda wf: wf[1], reverse=True)
            return [ wf[0] for wf in wordFreq ]
        else: return None


    def build(self):
        self.__initDataStructures()
        text2tokens = resolve(self.text2tokens)
        text2tokens.originalWords = True
        for txto in resolve(self.corpus):
            for token, word in text2tokens(txto.text):
                self.__register(token, word)
        # todo solve this problem, if only a single copy of the tokenizer exists
        # in the context, than originalWords should be reset back to false
        # because most of the use cases assume it is false, possible solution is copying
        text2tokens.originalWords = False

    def __register(self, token, word):
        ''' Add (word, token) data to data structures. '''
        if self.lowercase: word = word.lower()
        # increase word count for tokens
        if token not in self.token2words:
            self.token2words[token] = {}
        m = self.token2words[token]
        if word not in m: m[word]=1
        else: m[word] += 1
        # update max.freq. word
        if token not in self.topFreq: self.topFreq[token] = 0
        if m[word] > self.topFreq[token]:
            self.topFreq[token] = m[word]
            self.topWord[token] = word

    def save(self, folder): pickleObject(self, folder)

    def __getstate__(self):
        return self.lowercase, self.token2words, self.topFreq, self.topWord,  \
               IdComposer.__getstate__(self)

    def __setstate__(self, state):
        self.lowercase, self.token2words, self.topFreq, self.topWord, idcState = state
        IdComposer.__setstate__(self, idcState)


from pytopia.resource.ResourceBuilder import SelfbuildResourceBuilder
InverseTokenizerBuilder = SelfbuildResourceBuilder(InverseTokenizer)
