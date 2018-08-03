class Text2Tokens(object):
    '''
    Defines the interface of Text2Tokens-like objects.
    'id' is a mandatory attribute/property.
    '''

    def __call__(self, text):
        '''
        Returns list-like of string tokens for string text.
        '''

    @property
    def originalWords(self):
        '''
        Property that determines weather tokenizer returns tokens
         or (token, originalWord) pairs. False by default
        '''
        if hasattr(self, '_ow'): return self._ow
        else: return False

    @originalWords.setter
    def originalWords(self, ow): self._ow = ow