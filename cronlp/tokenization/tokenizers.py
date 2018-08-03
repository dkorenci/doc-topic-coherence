#-*-coding:utf-8-*-

'''
factory methods for tokenizers
'''

from cronlp.tokenization.RegexTokenizer import RegexTokenizer
from cronlp.utils.regex import croWord

def basicCroTokenizer():
    '''
    create simple tokenizer tokenizing text into
    (croatian) words, whitespaces and other tokens'
    '''
    regexes = {'whitespace':ur'\s+', 'word':croWord}
    return RegexTokenizer(wordTypes=set(['word']), wspaceTypes=set(['whitespace']), **regexes)

