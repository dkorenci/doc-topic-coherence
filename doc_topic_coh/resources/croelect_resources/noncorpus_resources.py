from doc_topic_coh.settings import croelect_models_folder, croelect_resources
from pytopia.context.Context import Context
from pytopia.resource.loadSave import loadResource
from pytopia.adapt.gensim.lda.GensimLdaModel import GensimLdaModel
from doc_topic_coh.resources.tools import FolderLocation

corpusId = 'iter0_cronews_final'
dictId = 'croelect_dict_iter0'
text2tokensId = 'CroelectTxt2Tokens'

def createWrappedCroelectModel(mid, folder):
    m = GensimLdaModel(None, id=mid)
    m.load(folder)
    m.corpus = corpusId
    m.dictionary = dictId
    m.text2tokens = text2tokensId
    return m

def croelectDictionary():
    d = loadResource(FolderLocation(croelect_resources)('dictionaries', 'croelect_dict'))
    return d

def croelectModelsContext():
    ctx = Context('croelect_models')
    folder = FolderLocation(croelect_models_folder)
    for f in ['model1', 'model2', 'model3', 'model4']:
        m = createWrappedCroelectModel('croelect_%s' % f, folder(f))
        ctx.add(m)
    return ctx

def croelectModelsIds():
    return ['croelect_%s' % f for f in ['model1', 'model2', 'model3', 'model4']]

def croelectMiscResourceContext():
    from doc_topic_coh.settings import cro_wiki_lucene
    ctx = Context('croelect_resources')
    ctx['crowiki_palmetto_index'] = cro_wiki_lucene
    from doc_topic_coh.resources.croelect_resources.preprocess import CroelectSwRemover
    from pytopia.nlp.text2tokens.gtar.text2tokens import alphanumStopwordsTokenizer
    crotok = alphanumStopwordsTokenizer(CroelectSwRemover())
    crotok.id = 'croelect_alphanum_stopword_tokenizer'
    ctx.add(crotok)
    return ctx

def croelectText2Tokens():
    from doc_topic_coh.resources.croelect_resources.preprocess import CroelectTxt2Tokens
    txt2tok = CroelectTxt2Tokens()
    txt2tok.id = text2tokensId
    return txt2tok

if __name__ == '__main__':
    #croelectModelsContext()
    #createWrappedCroelectDictionary()
    #croelectDictionary()
    #croelectOriginalModels()
    croelectText2Tokens()
