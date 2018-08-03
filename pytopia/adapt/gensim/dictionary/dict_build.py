from time import clock

from gensim.corpora import Dictionary

from pytopia.adapt.gensim.dictionary.GensimDictAdapter import GensimDictAdapter
from pytopia.context.ContextResolver import ContextResolver, resolveIds
from pytopia.tools.IdComposer import IdComposer


class GensimDictBuilder(ContextResolver):

    def __init__(self, ctx=None):
        self.context = ctx

    # pytopia resource builder interface
    def __call__(self, corpus, txt2tokens, opts):
        return self.buildDictionary(corpus, txt2tokens, opts)

    def resourceId(self, corpus, txt2tokens, opts):
        cid, t2tid = resolveIds(corpus, txt2tokens)
        return GensimDictAdapter(None, cid, t2tid, opts).id
    ###

    def buildDictionary(self, corpus, txt2tokens, opts):
        '''
        Tokenize texts and add tokens to dictionary.
        :param corpus: Corpus-like or id
        :param txt2tokens: txt2tokens or id
        :param opts: GensimDictBuildOptions
        :param ctx: pytopia context
        :return: gensim Dictionary
        '''
        t = clock()
        corpus, txt2tokens = self.resolve(corpus, txt2tokens)
        # fill the dictionary with tokens from corpus texts
        dictionary = Dictionary(documents=None)
        numDocs = 0; numTokens = 0
        for txto in corpus:
            tokens = txt2tokens(txto.text)
            numDocs += 1; numTokens += len(tokens)
            dictionary.doc2bow(tokens, allow_update=True)
        # form filtering options and run filtering
        no_below = opts.docLowerLimit if opts.docLowerLimit is not None else 0
        if opts.docUpperLimit is None: no_above = 1.0
        elif isinstance(opts.docUpperLimit, float): no_above = opts.docUpperLimit
        else: no_above = opts.docUpperLimit/float(numDocs)
        if opts.words2keep is None: keep_n = numTokens
        else: keep_n = opts.words2keep
        dictionary.filter_extremes(no_below=no_below, no_above=no_above,
                                   keep_n=keep_n)
        dictionary.compactify()
        # force id2token map building
        someId = dictionary.token2id.values()[0]
        dictionary[someId]
        return GensimDictAdapter(dictionary, corpus.id, txt2tokens.id, opts)

class GensimDictBuildOptions(IdComposer):

    def __init__(self, docLowerLimit, docUpperLimit, words2keep):
        '''
        :param docLowerLimit: words are removed if they don't occur
                in at least this many documents, if None filter is not applied
        :param docUpperLimit: words are removed if they occur in
                more than this many documents (integer or fraction),
                if None filter is not applied
        :param words2keep: after applying document filters, keep only this many words
        '''
        self.docLowerLimit = docLowerLimit
        self.docUpperLimit = docUpperLimit
        self.words2keep = words2keep
        IdComposer.__init__(self)