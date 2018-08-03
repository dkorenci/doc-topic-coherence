'''
text2tokens classes and other functionality originally created for the paper:
Getting the Agenda Right: Measuring Media Agenda using Topic Models
'''

from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer

from pytopia.nlp.text2tokens.Text2Tokens import Text2Tokens
from pytopia.nlp.text2tokens.regexp import wordTokenizer
from pytopia.nlp.text2tokens.gtar.stopwords import RsssuckerSwRemover

# todo test - compare on corpus equality with original tokenizer
class RsssuckerTxt2Tokens(Text2Tokens):
    '''
    Performs tokenization, stopword removal and stemming.
    '''

    def __init__(self, origWords=False):
        self.normalizer = TokenNormalizer(LemmatizerStemmer())
        self.swremover = RsssuckerSwRemover()
        self.tokenizer = wordTokenizer()
        self.originalWords = origWords

    @property
    def id(self): return self.__class__.__name__

    def tokenize(self, text):
        if not self.originalWords: return self.__tokenizeNonorig(text)
        else: return self.__tokenizeOrig(text)

    def __tokenizeNonorig(self, text):
        ''' return list of stems '''
        tokens = self.tokenizer.tokenize(text)
        return [ self.normalizer.normalize(tok) for tok in tokens if not self.swremover(tok) ]

    def __tokenizeOrig(self, text):
        ''' return list of (stem, originalWord) pairs '''
        tokens = self.tokenizer.tokenize(text)
        return [ (self.normalizer.normalize(tok), tok)
                    for tok in tokens if not self.swremover(tok) ]

    def __call__(self, text):
        return self.tokenize(text)



class TokenNormalizer():
    '''
    Base class for stemmers, lemmatizers, etc.
    Normalizers transform tokens to canonic form and keep a mapings from
    canonic forms to all the variations.
    '''
    def __init__(self, normFunct, storeVariants = False, lowercase = True):
        '''

        :param normFunct: string -> string function performing normalization
        :param storeVariants: it True store map of normalized form to unnormalized forms
        :param lowercase: it True, lowercasing will be performed by default before normFunct
        '''
        self.normFunct = normFunct; self.lowercase = lowercase
        self.storeVariants = storeVariants
        self.norm2token = {}

    def normalize(self, tok):
        from sets import Set
        tok = tok.lower() if self.lowercase else tok
        ntok = self.normFunct(tok)
        if self.storeVariants :
            if self.norm2token.has_key(ntok):
                self.norm2token[ntok].add(tok)
            else:
                s = Set(); s.add(tok)
                self.norm2token[ntok] = s
        return ntok

class PorterStemmerFunc():
    stemmer = PorterStemmer()
    def __call__(self, token):
        return PorterStemmerFunc.stemmer.stem(token)

class LemmatizerFunc():
    lemmatizer = WordNetLemmatizer()
    def __call__(self, token):
        return LemmatizerFunc.lemmatizer.lemmatize(token)

class LemmatizerStemmer():
    stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()
    def __call__(self, token):
        return LemmatizerStemmer.stemmer.stem(
            LemmatizerStemmer.lemmatizer.lemmatize(token))

# todo move out of .gtar package, this is more general functionality
def alphanumStopwordsTokenizer(swremover):
    '''
    Tokenizes into alphanumeric sequences, and applies stopword removal.
    :return:
    '''
    from pytopia.nlp.text2tokens.composite import CompositeText2Tokens
    from pytopia.nlp.text2tokens.regexp import alphanumTokenizer
    return CompositeText2Tokens(alphanumTokenizer(), swremover, None, True)
