from pytopia.context.Context import Context

def palmettoContext():
    from doc_topic_coh.settings import english_wiki_lucene
    ctx = Context('palmetto_context')
    ctx['wiki_docs'] = english_wiki_lucene
    return ctx
