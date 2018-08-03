from pytopia.tools.IdComposer import IdComposer
from pytopia.context.ContextResolver import resolve
from pytopia.resource.loadSave import pickleObject
from pytopia.tools.logging import resbuild_logger

@resbuild_logger
class CorpusIndexBuilder():

    def __init__(self, ctx=None):
        '''
        :param ctx: pytopia context
        '''
        self.__ctx = ctx

    def __call__(self, corpus):
        cindex = CorpusIndex(corpus)
        cindex.build()
        return cindex

    def resourceId(self, corpus):
        return CorpusIndex(corpus).id


class CorpusIndex(IdComposer):
    '''
    Fixed mapping between ids of texts in the corpus and
        integer indexes in [0, ... , NumTexts-1].
    Ensures fixed ordering of texts, in case
    the ordering varies between corpus traversals.
    '''

    def __init__(self, corpus):
        '''
        :param corpus: pytopia corpus or id
        '''
        self.corpus = resolve(corpus).id
        IdComposer.__init__(self)

    def __getitem__(self, index):
        ''' Return text id at specified position. '''
        return self.__index2id[index]

    def id2index(self, txtId):
        ''' Return index of the text with specified id. '''
        return self.__id2index[txtId]

    def __contains__(self, id_):
        '''True if id_ is indexed'''
        return id_ in self.__id2index

    def __iter__(self):
        ''' Iterate over corpus Ids, in order of increasing indexes. '''
        for i in range(self.__length): yield self.__index2id[i]

    def __len__(self):
        ''' Return number of ids in the index, which is also max. index '''
        return self.__length

    def __eq__(self, other):
        if not isinstance(other, self.__class__): return False
        if self.id != other.id: return False
        if len(self) != len(other): return False
        sids, oids = set(id for id in self), set(id for id in other)
        if sids != oids: return False
        for id in sids:
            if self.id2index(id) != other.id2index(id): return False
        return True


    ### build/save interface

    def build(self):
        self.__id2index, self.__index2id = {}, {}
        corpus = resolve(self.corpus)
        i = 0
        for txto in corpus:
            if txto.id not in self.__id2index:
                self.__id2index[txto.id] = i
                self.__index2id[i] = txto.id
                i += 1
        self.__length = i

    def save(self, folder): pickleObject(self, folder)

    def __getstate__(self):
        return self.__id2index, self.__index2id, self.__length, \
                IdComposer.__getstate__(self)

    def __setstate__(self, state):
        self.__id2index, self.__index2id, self.__length, idcState = state
        IdComposer.__setstate__(self, idcState)

