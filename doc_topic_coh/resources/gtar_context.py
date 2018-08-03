from doc_topic_coh.settings import uspol_models_folder
from pytopia.context.Context import Context
from pytopia.adapt.gensim.lda.GensimLdaModel import GensimLdaModel

from os import path


modelId2Folder = {
    'uspolM0' : 'uspolM0_234_ldamodel_T50_A1.000_Eta0.010_Off1.000_Dec0.500_Chunk1000_Pass10_label_seed345556',
    'uspolM1' : 'uspolM1_234_ldamodel_T50_A1.000_Eta0.010_Off1.000_Dec0.500_Chunk1000_Pass10_label_seed877312',
    'uspolM2' : 'uspolM2_234_ldamodel_T50_A1.000_Eta0.010_Off1.000_Dec0.500_Chunk1000_Pass10_label_seed8903',
    'uspolM10' : 'uspolM10_045_ldamodel_T100_A0.500_Eta0.010_Off1.000_Dec0.500_Chunk1000_Pass10_label_seed345556',
    'uspolM11' : 'uspolM11_045_ldamodel_T100_A0.500_Eta0.010_Off1.000_Dec0.500_Chunk1000_Pass10_label_seed133890'
}

def gtarDictionaryContext():
    from doc_topic_coh.settings import uspol_resources
    from doc_topic_coh.resources.tools import FolderLocation
    from pytopia.utils.load import listSubfolders
    from pytopia.resource.loadSave import loadResource
    f = FolderLocation(uspol_resources)('dictionaries')
    ctx = {}
    for sf in listSubfolders(f):
        dict = loadResource(sf)
        ctx[dict.id] = dict
    return ctx

def gtarText2TokensContext():
    from pytopia.nlp.text2tokens.gtar.text2tokens import RsssuckerTxt2Tokens
    from pytopia.nlp.text2tokens.regexp import alphanumTokenizer
    from pytopia.nlp.text2tokens.gtar.text2tokens import alphanumStopwordsTokenizer
    from pytopia.nlp.text2tokens.gtar.stopwords import RsssuckerSwRemover
    ctx = Context('gtar_text2tokens_context')
    ctx.add(RsssuckerTxt2Tokens())
    ctx.add(alphanumTokenizer())
    alphasw = alphanumStopwordsTokenizer(RsssuckerSwRemover())
    alphasw.id = 'alphanum_gtar_stopword_tokenizer'
    ctx.add(alphasw)
    return ctx

def createWrappedGensimModel(mid, folder):
    m = GensimLdaModel(None, id=mid)
    m.load(folder)
    m.corpus = 'us_politics'
    m.dictionary = 'us_politics_dict'
    m.text2tokens = 'RsssuckerTxt2Tokens'
    return m

def gtarModelsContext():
    ctx = Context('gtar_models_context')
    for mid, mfolder in modelId2Folder.iteritems():
        f = path.join(uspol_models_folder, mfolder)
        ctx.add(createWrappedGensimModel(mid, f))
    return ctx

if __name__ == '__main__':
    print gtarModelsContext()
