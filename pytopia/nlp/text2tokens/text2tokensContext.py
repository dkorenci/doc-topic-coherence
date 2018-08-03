from pytopia.context.Context import Context

from pytopia.nlp.text2tokens.regexp import whitespaceTokenizer, alphanumTokenizer, wordTokenizer

def basicTokenizersContext():
    ctx = Context('basic_tokenizers')
    ctx.add(whitespaceTokenizer())
    ctx.add(alphanumTokenizer())
    ctx.add(wordTokenizer())
    return ctx
