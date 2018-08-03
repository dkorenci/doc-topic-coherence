from pytopia.resource.FolderResourceCache import FolderResourceCache
from doc_topic_coh.settings import resource_cache
from doc_topic_coh.resources.tools import FolderLocation

resource_cache_folder = FolderLocation(resource_cache)

def corpusIndexBuilder():
    from pytopia.resource.corpus_index.CorpusIndex import CorpusIndexBuilder
    return FolderResourceCache(CorpusIndexBuilder(),
                               resource_cache_folder.subfolder('corpus_index'),
                               id = 'corpus_index_builder')

def corpusTfidfBuilder():
    from pytopia.resource.corpus_tfidf.CorpusTfidfIndex import CorpusTfidfBuilder
    return FolderResourceCache(CorpusTfidfBuilder(),
                               resource_cache_folder.subfolder('corpus_tfidf_index'),
                               id = 'corpus_tfidf_builder')

def corpusTopicIndexBuilder():
    from pytopia.resource.corpus_topics.CorpusTopicIndex import CorpusTopicIndexBuilder
    return FolderResourceCache(CorpusTopicIndexBuilder(),
                               resource_cache_folder.subfolder('corpus_topic_index'),
                               id = 'corpus_topic_index_builder')

def bowCorpusBuilder():
    from pytopia.resource.bow_corpus.bow_corpus import BowCorpusBuilder
    return FolderResourceCache(BowCorpusBuilder(),
                               resource_cache_folder.subfolder('bow_corpus'),
                               id = 'bow_corpus_builder')

def wordDocIndexBuilder():
    from pytopia.resource.worddoc_index.worddoc_index import WordDocIndexBuilder
    return FolderResourceCache(WordDocIndexBuilder(),
                               resource_cache_folder.subfolder('worddoc_index'),
                               id = 'worddoc_index_builder')

def word2vecBuilder():
    from pytopia.resource.word2vec.word2vec import Word2VecBuilder
    return FolderResourceCache(Word2VecBuilder,
                               resource_cache_folder.subfolder('word2vec'),
                               id = 'word2vec_builder')

def gloveVecBuilder():
    from pytopia.resource.glove_vectors.glove import GloveVectorsBuilder
    return FolderResourceCache(GloveVectorsBuilder,
                               resource_cache_folder.subfolder('glove'),
                               id = 'glove_vectors_builder')

def inverseTokenizerBuilder():
    from pytopia.resource.inverse_tokenization.InverseTokenizer import InverseTokenizerBuilder
    return FolderResourceCache(InverseTokenizerBuilder,
                               resource_cache_folder.subfolder('inverse_tokenization'),
                               id = 'inverse_tokenizer_builder')

def corpusTextVectorsBuilder():
    from pytopia.resource.corpus_text_vectors.CorpusTextVectors import CorpusTextVectorsBuilder
    return FolderResourceCache(CorpusTextVectorsBuilder,
                               resource_cache_folder.subfolder('corpus_text_vectors'),
                               id = 'corpus_text_vectors_builder')
