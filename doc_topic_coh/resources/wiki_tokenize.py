from sqlalchemy import create_engine
#engine = create_engine("mysql://jwpl@localhost/jwpl_core_en20150602", echo=False)
engine = create_engine("mysql://jwpl@localhost/jwpl_core_hr20171103", echo=False)
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import LONGTEXT

from pytopia.nlp.text2tokens.gtar.text2tokens import RsssuckerTxt2Tokens
from doc_topic_coh.resources.croelect_resources.preprocess import CroelectTxt2Tokens

class PageExt(Base):
    __tablename__ = 'page_ext'
    id = Column(Integer, primary_key=True)
    plainText = Column(LONGTEXT)
    name = Column(String)

class PageExtTok(Base):
    __tablename__ = 'page_ext_tok'
    id = Column(Integer, primary_key=True)
    text = Column(LONGTEXT)

Base.metadata.create_all(engine)

def test():
    session = Session()
    for obj in session.query(PageExt.id, PageExt.plainText).filter(PageExt.id.in_([12,25])):
        print obj.id
        print obj.plainText

def selectIds(numChunks=1, rawIds=None):
    '''Fetch a list of all ids from PageExt table and break into equal sized chunks. '''
    from array import array
    session = Session()
    processedIds = set(o.id for o in session.query(PageExtTok.id))
    if rawIds:
        ids = [o.id for o in session.query(PageExt.id).filter(PageExt.id.in_(rawIds))]
    else: # get all ids from the table
        ids = array('L', [o.id for o in session.query(PageExt.id)])
    ids = [ id for id in ids if id not in processedIds ]
    ids = array('L', ids)
    print 'numIds', len(ids)
    if numChunks > 1:
        L = len(ids); cl = L / numChunks;
        chunks = []
        for i in range(numChunks):
            start = i*cl
            if i == numChunks - 1: end = L
            else: end = (i+1)*cl
            chunks.append(ids[start:end])
        s = sum(len(c) for c in chunks)
        print 'chunk lens sum: %d' %s
        assert s == len(ids)
        assert(set(ids) == set(id for c in chunks for id in c))
        return chunks
    else: return ids

from sys_utils.multiprocess import unpinProcess
import sys
from traceback import print_exception
from logging_utils.setup import *
from logging_utils.tools import fullClassName

log = createLogger('wiki_tokenize', INFO)
class TokenizerProcessor():
    '''
    Tokenizes plain texts from PageExt table and saves them in the 'tokenized'
    '''
    def __init__(self, tok):
        self.tokenizer = tok

    def __call__(self, ids):
        try:
            self.__processIds(ids)
        except:
            from StringIO import StringIO
            log.error('processing of ids %s failed' % str(ids[:20]))
            sio = StringIO()
            e = sys.exc_info()
            print_exception(e[0], e[1], e[2], file=sio)
            log.error(sio.getvalue())

    def __processIds(self, ids):
        '''
        :param ids: list of PageExt ids to process
        '''
        print 'processing chunk', ids[:10]
        unpinProcess()
        session = Session()
        for pe in session.query(PageExt).filter(PageExt.id.in_(ids)):
            tl = [ self.tokenizer(l) for l in pe.plainText.splitlines() ]
            res = u'\n'.join(u' '.join(l) for l in tl)
            pet = PageExtTok(id=pe.id, text=res)
            session.add(pet)
        session.commit()
        session.close()
        print 'done processing ', ids[:10]

testIdSet = [12,25,39,290,303,305, 307,308,309,316,324]
def processPages(numProcesses, numChunks, text2tokens):
    # ALTER TABLE page_ext ADD uspolTokens longtext;
    from multiprocessing import Pool
    processor = TokenizerProcessor(text2tokens)
    idChunks = selectIds(numChunks)
    if numProcesses > 1:
        p = Pool(numProcesses)
        p.map(processor, idChunks)
    else:
        print 'serial'
        for ch in idChunks:
            processor(ch)

def analyzeShortPages(maxLength, sampleSize=None, rseed=6778):
    '''
    Print (a sample of) pages with tokenized length less than maxLength.
    '''
    from sqlalchemy.sql.expression import func, and_
    from random import sample, seed
    session = Session()
    if isinstance(maxLength, tuple): mn, mx = maxLength
    else: mn = 0; mx = maxLength
    res = [o for o in session.query(PageExtTok).filter(
                and_(func.length(PageExtTok.text) >= mn, func.length(PageExtTok.text) <= mx)
            )]
    print len(res)
    if sampleSize and sampleSize < len(res):
        seed(rseed)
        res = sample(res, sampleSize)
    ids = set(pet.id for pet in res)
    origTxt = [o for o in session.query(PageExt).filter(PageExt.id.in_(ids))]
    oId2Txt = { o.id : o for o in origTxt }
    for t in res:
        orig = oId2Txt[t.id]
        print t.id, orig.name, len(orig.plainText)
        print u'text = [%s]' % orig.plainText.strip()

def tokenizedWikiToTxtFile(outfile, windowSize = 1000, flushEvery=10000):
    import codecs
    session = Session()
    f = codecs.open(outfile, 'w', 'utf8')
    q = session.query(PageExtTok)
    windowIndex = 0; pagesLoaded = 0
    idSet = set()
    while True:
        start, stop = windowSize * windowIndex, windowSize * (windowIndex + 1)
        result = q.slice(start, stop).all()
        if result is None: break
        for pe in result:
            if pe.id in idSet:
                print '!!! duplicate fetch', pe.id
                continue
            else: idSet.add(pe.id)
            txt = pe.text.strip()
            if len(txt) > 0:
                f.write(pe.text); f.write('\n')
            pagesLoaded += 1
            if pagesLoaded % flushEvery == 0:
                f.flush()
                print 'processed %d' % pagesLoaded
        if len(result) < windowSize: break
        windowIndex += 1
    print 'pages loaded: %d' % pagesLoaded
    f.close()
    session.close()

if __name__ == '__main__':
    #test()
    #selectAllIds(3)
    #processPages(1, 30, CroelectTxt2Tokens())
    #analyzeShortPages((0, 50), 100, 8891)
    tokenizedWikiToTxtFile('/datafast/hrwiki/wiki_hr20171103_croelect_tokenization.txt')