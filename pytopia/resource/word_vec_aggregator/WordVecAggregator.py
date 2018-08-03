from pytopia.context.ContextResolver import resolve, resolveIds
from pytopia.tools.IdComposer import IdComposer

import numpy as np

#TODO tests
class WordVecAggregator(IdComposer):
    '''
    Vectorizes texts by aggregating word vectors.
    '''

    def __init__(self, text2tokens, word2vector, tokenMod=None, avg=None):
        # todo remove tokenMod, clients should use function composition insted
        # todo solve passing params by id
        self.text2tokens, self.word2vector = text2tokens, word2vector
        self.tokenMod = tokenMod; self.avg = avg
        IdComposer.__init__(self)

    def __call__(self, txto):
        textVec = None
        txt2tok = resolve(self.text2tokens)
        vecnt = 0
        for tok in txt2tok(txto.text):
            if self.tokenMod is not None:
                tok = self.tokenMod(tok)
            vec = self.word2vector(tok)
            if vec is None: continue
            if not isinstance(vec, np.ndarray): raise Exception('unsupported vector type')
            if textVec is None:
                textVec = vec.copy(); vecnt = 1
            else:
                textVec += vec; vecnt += 1
        if self.avg: textVec /= vecnt
        return textVec
