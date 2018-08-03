'''
Initializer of global context for the pycoverexp project.
To init the context, import module.
'''

from pytopia.context.GlobalContext import GlobalContext
from pytopia.context.Context import Context
from pytopia.context.ContextResolver import resolve

__contextSet = False

def __initContext():
    global __contextSet
    if __contextSet: return
    GlobalContext.set(__pycoverexpContext())

from doc_topic_coh.resources.gtar_context import gtarModelsContext, \
    gtarDictionaryContext, gtarText2TokensContext
from doc_topic_coh.resources.gtar_corpus import getGtarCorpusContext
from doc_topic_coh.resources.builders_context import *
from doc_topic_coh.resources.misc_resources_context import palmettoContext
from doc_topic_coh.resources.croelect_resources.noncorpus_resources import croelectDictionary, \
            croelectText2Tokens, croelectModelsContext, croelectMiscResourceContext
from doc_topic_coh.resources.croelect_resources.corpus import getCroelectCorpusContext

def __pycoverexpContext():
    ctx = Context('doc_topic_coherence_context')
    ctx.merge(getGtarCorpusContext())
    ctx.merge(gtarDictionaryContext())
    ctx.merge(gtarModelsContext())
    ctx.merge(gtarText2TokensContext())
    ctx.merge(palmettoContext())
    ctx.add(corpusIndexBuilder())
    ctx.add(corpusTfidfBuilder())
    ctx.add(corpusTopicIndexBuilder())
    ctx.add(wordDocIndexBuilder())
    ctx.add(bowCorpusBuilder())
    ctx.add(word2vecBuilder())
    ctx.add(gloveVecBuilder())
    ctx.add(inverseTokenizerBuilder())
    ctx.add(corpusTextVectorsBuilder())
    # croelect resources
    ctx.merge(getCroelectCorpusContext())
    ctx.merge(croelectModelsContext())
    ctx.merge(croelectMiscResourceContext())
    ctx.add(croelectDictionary())
    ctx.add(croelectText2Tokens())
    return ctx

__initContext()

def printContext():
    print unicode(__pycoverexpContext())

if __name__ == '__main__':
    printContext()

