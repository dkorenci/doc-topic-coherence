class TextsizeFilter():
    '''
    Filters out texts with less then certain number of tokens.
    '''

    def __init__(self, textSize, tokenizer):
        self.tokenizer = tokenizer
        self.textSize = textSize
        self.id = 'TextsizeFilter[size:%s][tokenizer:%s]' % \
                  (str(textSize), str(tokenizer.id))

    def __call__(self, txtobj):
        if len(txtobj.text) == 0 : return True
        if len(self.tokenizer(txtobj.text)) < self.textSize  : return True