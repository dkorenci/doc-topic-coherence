from gensim.corpora.dictionary import Dictionary as GensimDict
from pytopia.dictionary.Dictionary import Dictionary
from pytopia.tools.IdComposer import IdComposer
from pytopia.resource.loadSave import pickleObject

from os import path
import cPickle, os

class GensimDictAdapter(IdComposer, Dictionary):
    '''Gensim dictionary 2 pytopia dictionary adapter'''

    def __init__(self, gensimDict, corpusId=None, txt2tokId=None, opts=None, id=None):
        '''
        :param gensimDict: Dictionary object
        :param buildOpts: GensimDictBuildOptions
        '''
        # setup id attributes
        self.corpusId = corpusId
        self.txt2tokId = txt2tokId
        self.buildOpts = opts
        IdComposer.__init__(self, attributes =
            ['corpusId', 'txt2tokId', 'buildOpts'])
        self.id = id
        # setup dict attributes
        if gensimDict is not None:
            if not isinstance(gensimDict, GensimDict):
                Exception('must be initialized with gensim Dictionary object')
        self.__dict = gensimDict

    @property
    def wrapped(self):
        try: return self.__dict
        except: return None

    def __len__(self): return len(self.__dict)

    def tokens2bow(self, tokens): return self.__dict.doc2bow(tokens)

    def token2index(self, token): return self.__dict.token2id[token]

    def index2token(self, index): return self.__dict.id2token[index]

    def __contains__(self, token): return token in self.__dict.token2id

    def iteritems(self): return self.__dict.token2id.iteritems()

    def iterkeys(self): return self.__dict.token2id.iterkeys()

    def itervalues(self): return self.__dict.token2id.itervalues()

    def save(self, folder):
        pickleObject(self, folder)
        self.__dict.save(path.join(folder, self.__gensimFname()))

    def load(self, folder):
        self.__dict = GensimDict.load(path.join(folder, self.__gensimFname()))

    def __gensimFname(self): return 'gensimDict'

