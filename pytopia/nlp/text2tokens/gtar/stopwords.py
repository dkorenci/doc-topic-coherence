from sets import Set

from nltk.corpus import stopwords
from pytopia.nlp.text2tokens.regexp import wordTokenizer

from os import path

def rsssucker_stopwords():
    'construct stopword list for rsssucker corpus, to be used with regex_word_tokenizer '
    # read snowball stemmer sw list
    snowball_stopwords = path.join(path.dirname(__file__),
                                   'snowball.stopwords.en.txt')
    sw_list = [ line.strip().lower() for line in
                open(snowball_stopwords).readlines() if line.strip() != '' ]
    # add nltk stopwords
    for sw in stopwords.words('english'): sw_list.append(sw.lower())
    #tokenize stopwords and add tokens, because the list will be applied
    #after tokenization and the tokenizer splits words with 's in parts
    sw_set = Set()
    tok = wordTokenizer()
    for sw in sw_list:
        for t in tok.tokenize(sw):
            sw_set.add(t)
    #add single letters
    for c in 'abcdefghijklmnopqrstuvwxyz' : sw_set.add(c)
    #add corpus specific stopwords
    rss_stopwords = ['http', 'say', 'said', 'th', 'ii', 'jr', 'dr', 'mr', 'www']
    for sw in rss_stopwords: sw_set.add(sw)
    return sw_set

class RsssuckerSwRemover():
    stwords = rsssucker_stopwords()

    def __init__(self):
        self.id = 'rsssucker_stopword_remover'

    def __call__(self, token):
        return token.lower() in RsssuckerSwRemover.stwords

    def remove(self, tokenList):
        'return list with stopword tokens removed'
        return [ tok for tok in tokenList if tok.lower() not in RsssuckerSwRemover.stwords ]