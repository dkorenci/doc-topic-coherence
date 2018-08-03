from pytopia.tools.IdComposer import IdComposer
from pytopia.context.ContextResolver import resolve, resolveIds

import numpy as np

class TextProbVectorizer(IdComposer):
    '''
    Converts text to bag-of-words vector with word frequencies
     normalized to probabilities as coordinate values.
    '''

    def __init__(self, text2tokens, dictionary):
        self.text2tokens, self.dictionary = resolveIds(text2tokens, dictionary)
        IdComposer.__init__(self)

    def __call__(self, txto):
        d, t2t = resolve(self.dictionary, self.text2tokens)
        vec = np.zeros(d.maxIndex()+1, np.float32)
        numTokens = 0
        for tok in t2t(txto.text):
            if tok in d:
                vec[d.token2index(tok)] += 1
                numTokens += 1
        vec /= numTokens
        return vec
