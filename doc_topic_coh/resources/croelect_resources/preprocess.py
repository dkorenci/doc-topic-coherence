from cronlp.stopwords.stopwords import croStopwords
from cronlp.tokenization.tokenizers import basicCroTokenizer
from cronlp.stemming.ffzg_crostemmer.cro_stemmer_interface import stemWord

def croelectStopwords():
    '''
    Construct and return a set of stopwords.
    '''
    swords = croStopwords()
    newswords = u'a b c ć č d đ e f g h i j k l m n o p q r s š t u v z ž www com http hr'
    allswords = set()
    for s in swords: allswords.add(s.lower())
    for s in newswords.split(): allswords.add(s)
    return allswords

class CroelectSwRemover():
    stwords = croelectStopwords()

    def __init__(self):
        self.id = 'croelect_stopword_remover'

    def __call__(self, token):
        return token.lower() in CroelectSwRemover.stwords

    def remove(self, tokenList):
        'return list with stopword tokens removed'
        return [ tok for tok in tokenList if tok.lower() not in CroelectSwRemover.stwords ]

def stemHyphenEnding(word):
    '''
    removes -X from the end of the word, where X is
    emtpy or an ending "a", "i", "im",
    '''
    if not '-' in word: return word
    endings = '- -a -e -i -u -ov -im -ovim -ovu'
    for e in endings.split():
        #print '[%s]'%e
        if word.endswith(e): return word[:-len(e)]
    return word

class CroelectTxt2Tokens():

    def __init__(self):
        self.swords = croelectStopwords()
        self.tokenizer = basicCroTokenizer()

    def tokenize(self, text):
        return [ stemHyphenEnding(stemWord(tok)) for tok in self.tokenizer.wordStringTokens(text)
                    if not tok.lower() in self.swords ]

    def __call__(self, text):
        return self.tokenize(text)
