from pytopia.context.Context import Context
from pytopia.resource.builder_cache.ResourceBuilderCache import ResourceBuilderCache

from file_utils.location import FolderLocation

from pytopia.resource.corpus_index.CorpusIndex import CorpusIndexBuilder
from pytopia.resource.corpus_tfidf.CorpusTfidfIndex import CorpusTfidfBuilder
from pytopia.resource.corpus_topics.CorpusTopicIndex import CorpusTopicIndexBuilder
from pytopia.resource.bow_corpus.bow_corpus import BowCorpusBuilder
from pytopia.resource.worddoc_index.worddoc_index import WordDocIndexBuilder
from pytopia.resource.inverse_tokenization.InverseTokenizer import InverseTokenizerBuilder
from pytopia.resource.corpus_text_vectors.CorpusTextVectors import CorpusTextVectorsBuilder

# todo move FolderLocation to pytopia
def basicBuildersContext(cacheFolder):
    '''
    Create context with cached basic resource builders.
    Cache folders of the builders are subfolders of the cacheFolder
     named after the resource type.
    '''
    ctx = Context('pytopia_basic_builders_context')
    cf = FolderLocation(cacheFolder)
    ctx.add(cachedResourceBuilder(
            CorpusIndexBuilder(), cf('corpus_index'), id='corpus_index_builder'))
    ctx.add(cachedResourceBuilder(
        WordDocIndexBuilder(), cf('worddoc_index'), id='worddoc_index_builder'))
    ctx.add(cachedResourceBuilder(
        BowCorpusBuilder(), cf('bow_corpus'), id='bow_corpus_builder'))
    ctx.add(cachedResourceBuilder(
        CorpusTfidfBuilder(), cf('corpus_tfidf_index'), id='corpus_tfidf_builder'))
    ctx.add(cachedResourceBuilder(
        CorpusTextVectorsBuilder, cf('corpus_text_vectors'), id='corpus_text_vectors_builder'))
    ctx.add(cachedResourceBuilder(
        CorpusTopicIndexBuilder(), cf('corpus_topic_index'), id='corpus_topic_index_builder'))
    ctx.add(cachedResourceBuilder(
        InverseTokenizerBuilder, cf('inverse_tokenization'), id='inverse_tokenizer_builder'))
    return ctx

def cachedResourceBuilder(builder, cacheFolder, id):
    return ResourceBuilderCache(builder, cacheFolder, id=id)
