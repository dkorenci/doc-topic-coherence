from pytopia.tools.IdComposer import IdComposer

class CompositeText2Tokens(IdComposer):
    '''
    Applies token-filtering (ie stopword removal) and
    post-tokenization token transformation (ie normalization) to a given tokenizer.
    '''

    # todo implement general filter/transformer chain
    def __init__(self, text2tokens, filter, transformer, lowercase=False):
        '''
        :param filter: callable, accepts a string token, returns True (filter out) or False (keep token)
        :param transformer: callable, accepts a string token, returns a string
        '''
        self.text2tokens = text2tokens
        self.filter, self.transformer = filter, transformer
        if lowercase: self.lowercase = True
        IdComposer.__init__(self)
        self.lowercase = lowercase

    def __call__(self, text):
        ''' return list of stems '''
        tokens = self.text2tokens(text)
        low = lambda tok: tok.lower() if self.lowercase else tok
        trans = (lambda tok: low(self.transformer(tok))) \
                if self.transformer else (lambda tok: low(tok))
        filter = (lambda tok: self.filter(tok)) if self.filter else (lambda tok: False)
        return [ trans(tok) for tok in tokens if not filter(tok) ]