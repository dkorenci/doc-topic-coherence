import re

def wordTokenizer():
    '''Select tokens of english alphabet strings, possibly with one hyphen in the middle'''
    return RegexpTokenizer('english_word_tokenizer', '([a-zA-Z]+)(\-[a-zA-Z]+)?')

def alphanumTokenizer():
    '''Select alphanumeric tokens (english alphabet).'''
    return RegexpTokenizer('english_alphanum_tokenizer', '[a-zA-Z0-9]+')

def whitespaceTokenizer():
    ''' Tokenize into sequences of non-whitespace characters. '''
    return RegexpTokenizer('whitespace_tokenizer', '\S+')

class RegexpTokenizer():
    '''
    Extract tokens that match a regular expression.
    '''

    def __init__(self, id, pattern):
        self.id = id
        self.__init_object(pattern)
        self.__init_merge()

    def __init_merge(self):
        self.merge = lambda o: ''.join(o) if isinstance(o, tuple) else o

    def tokenize(self, text):
        if not hasattr(self, 'merge'): self.__init_merge()
        return [self.merge(o) for o in self.regex.findall(text)]

    def __call__(self, text): return self.tokenize(text)

    def __init_object(self, pattern):
        self.pattern = pattern
        self.regex = re.compile(pattern, flags=re.UNICODE|re.MULTILINE|re.DOTALL)

    def __getstate__(self):
        return self.pattern

    def __setstate__(self, pattern):
        self.__init_object(pattern)

def testTokenizers():
    tok = whitespaceTokenizer()
    print tok('a b c d')

if __name__ == '__main__':
    testTokenizers()