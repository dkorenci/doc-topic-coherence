from gensim.corpora.dictionary import Dictionary as GensimDict
from pytopia.context.ContextResolver import resolve

def pytopia2gensimDict(dict_):
    '''
    Creates gensim dictionary from a pytopia dictionary.
    This is necessary since building of gensim models requires gensim dictionary
     but pytopia model builders must be able to receive generic pytopia Dictionary as parameter.
    '''
    # sort dictionary tokens by index
    dict_ = resolve(dict_)
    toki = [(tok, dict_[tok]) for tok in dict_]
    toki.sort(key=lambda ti: ti[1])
    # directly set gensim dict data structures,
    # this works for gensim 0.12.4
    gdict = GensimDict()
    gdict.token2id = { tok:i for tok, i in toki }
    gdict.id2token = { i:tok for tok, i in toki }
    gdict.dfs = { tok:1 for tok, _ in toki }
    gdict.num_docs = 1  # number of documents processed
    gdict.num_pos = len(toki)  # total number of corpus positions
    gdict.num_nnz = len(toki)  # total number of non-zeroes in the BOW matrix
    return gdict
