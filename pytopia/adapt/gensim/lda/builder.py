from pytopia.tools.IdComposer import IdComposer
from pytopia.adapt.gensim.lda.ldamodel_mod import LdaModel
from pytopia.adapt.gensim.lda.GensimLdaModel import GensimLdaModel
from pytopia.adapt.gensim.dictionary.pytopia2gensim import pytopia2gensimDict
from pytopia.tools.logging import resbuild_logger

from pytopia.context.ContextResolver import resolve

@resbuild_logger
class GensimLdaModelBuilder():

    def __init__(self, ctx=None):
        '''
        :param ctx: pytopia context
        '''
        self.__ctx = ctx

    def __call__(self, corpus, dictionary, text2tokens, options):
        '''
        :param corpus: pytopia corpus
        :param dictionary: pytopia dictionary, with gensim dictionary as 'wrapped' attribute
        :param txt2tokens: pytopia text2tokens
        :param options: GensimLdaOptions
        :return:
        '''
        corpus, dictionary, txt2tokens = \
            resolve(corpus, dictionary, text2tokens, context=self.__ctx)
        bowBuilder = resolve('bow_corpus_builder', context=self.__ctx)
        bowCorpus = bowBuilder(corpus, txt2tokens, dictionary)
        # todo create tests for non-wrapped building case
        if hasattr(dictionary, 'wrapped'):
            gensimModel = options.getModel(dictionary.wrapped)
        else:
            gensimModel = options.getModel(pytopia2gensimDict(dictionary))
        gensimModel.update(bowCorpus)
        model = GensimLdaModel(gensimModel)
        model.corpus, model.dictionary, model.text2tokens, model.options = \
            corpus.id, dictionary.id, txt2tokens.id, options
        return model

    def resourceId(self, corpus, dictionary, text2tokens, options):
        model = GensimLdaModel(None)
        corpus, dictionary, txt2tokens = \
            resolve(corpus, dictionary, text2tokens, context=self.__ctx)
        model.corpus, model.dictionary, model.text2tokens, model.options = \
            corpus.id, dictionary.id, txt2tokens.id, options
        return model.id

class GensimLdaOptions(IdComposer):
    '''
    Hyperparams and other options for initializing LdaModel
    '''

    def __init__(self, numTopics, alpha, eta, offset, decay, chunksize, passes,
                 seed = 12345, alphaInit = None):
        self.numTopics = numTopics
        self.alpha = alpha; self.alphaInit = alphaInit
        self.eta = eta; self.offset = offset
        self.decay = decay; self.chunksize = chunksize
        self.passes = passes; self.seed = seed
        IdComposer.__init__(self)

    def getModel(self, dictionary):
        ''' Create new LdaModel set up with options from self and with given dictionary. '''
        return LdaModel(id2word=dictionary, num_topics=self.numTopics, alpha=self.alpha,
                        alpha_init=self.alphaInit, eta=self.eta, offset=self.offset,
                        decay=self.decay, chunksize=self.chunksize, passes=self.passes,
                        seed = self.seed)
