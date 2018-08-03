from pytopia.corpus.Text import Text
from pytopia.corpus.text.TextPerLineCorpus import TextPerLineCorpus
from pytopia.corpus.text.TextCorpus import TextCorpus

#TODO move hard line syntax cases to parseLine tests
#TODO  and fix multiple commas case
corpusData = {
    'rawText':
    ur'''
    id = 0, att = abcd, text = some, text
    id = 1, att = a\,b\,c\,a , text = text=now,
    ''',
    'texts': [Text('0', u' some, text', att='abcd'),
              Text('1', u' text=now,', att=u'a,b,c,a')]
}

def assertTextEquality(txt1, txt2):
    assert txt1.id == txt2.id
    assert txt1.text == txt2.text
    #TODO assert equaility for other attributes

def singleCorpusCheck(cClass, params, texts):
    corpus = cClass(**params)
    for i, txto in enumerate(corpus):
        ctxt = texts[i]
        assertTextEquality(txto, ctxt)

def stringToFile(string, file):
    '''
    Store string to file and return file name
    :param file: string path or py.path.local
    '''
    import codecs
    with codecs.open(str(file), 'w', 'utf-8') as f:
        f.write(string)
    return str(file)

def test_corpora(tmpdir):
    singleCorpusCheck(TextCorpus, {'id':None, 'text':corpusData['rawText']},
                        corpusData['texts'])
    singleCorpusCheck(TextPerLineCorpus,
                      {'file': stringToFile(corpusData['rawText'], tmpdir.join('corpus.txt'))},
                        corpusData['texts'])
