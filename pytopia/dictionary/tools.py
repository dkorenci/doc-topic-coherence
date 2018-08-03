from gensim.corpora.dictionary import Dictionary
from pytopia.adapt.gensim.dictionary.GensimDictAdapter import GensimDictAdapter
from pytopia.resource.loadSave import saveResource

from os import path

def wrapGensimDictionary(dictFile, storeFolder, id):
    '''Wrap gensim dict from file in GensimDictAdapter, store the adapter. '''
    dict = Dictionary.load(dictFile)
    adict = GensimDictAdapter(dict); adict.id = id
    saveResource(adict, path.join(storeFolder, id))

