'''
legacy functionality developed for Getting The Agenda Right paper
'''

from pytopia.corpus.Text import Text
from pytopia.corpus.Corpus import Corpus

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import random

class FeedsuckerCorpus(Corpus):
    '''
    Corpus that reads text documents from postgres database created by
    Feedsucker (legacy name Rsssucker) application:
     https://github.com/dkorenci/feedsucker
    '''

    def __init__(self, dbName, uname='rsssucker', pword='rsssucker', id = None):
        self._dbname = dbName; self._uname = uname ; self._password = pword
        self.__id = id
        self._dbConnected = False

    def _initDB(self):
        if self._dbConnected : return
        conn_str = "postgresql+psycopg2://%s:%s@localhost/%s"%\
                   (self._uname, self._password, self._dbname)
        self._engine = create_engine(conn_str)
        self._session_maker = sessionmaker(bind=self._engine)
        # todo thread safety of one global session?
        self._session = self._session_maker()
        self._dbConnected = True

    @property
    def id(self):
        if self.__id is not None: return self.__id
        else: return self._dbname

    def textIds(self):
        ''' Read all text ids from the database. '''
        self._initDB()
        session = self._session_maker()
        for id in session.query("id").execution_options(stream_result=True).\
                    from_statement(text("SELECT id FROM feedarticle")).all() :
            yield id[0]
        session.close()

    def getTexts(self, id_list):
        self._initDB()
        "yield (id, text) pairs for text with specified ids"
        # create list of ids for sql query
        if len(id_list) == 0 : return
        id_str = "(";
        for id in id_list : id_str += (str(id)+',')
        id_str = id_str[:-1]; id_str += ')'
        query = "SELECT id, text, feedtitle FROM feedarticle WHERE id IN %s" % id_str
        session = self._session #self._session_maker()
        for id, txt, title in session.query("id","text","feedtitle").\
                    execution_options(stream_result=True).from_statement(text(query)).all() :
            txt = Text(id, txt, title=title)
            yield txt
        #session.close()

    def getFeeds(self, txto):
        '''
        Fetch list of urls of feeds containing this text.
        "Save" to txto.feedUrls property
        '''
        template = '''
        SELECT DISTINCT feed.url FROM feed
        LEFT JOIN feedarticle_feed ff ON ff.feeds_id = feed.id
        WHERE articles_id = %d
        '''
        self._initDB()
        session = self._session_maker()
        query = template % txto.id
        result = []
        for url in session.query('url').execution_options().from_statement(text(query)).all():
            result.append(url[0])
        session.close()
        txto.feedUrls = result

    def getOutlets(self, txto):
        '''
        Fetch list of names of outlets containing this text.
        "Save" to txto.outlets property
        '''
        template = '''
        select distinct o.name from outlet o
        left join feed f on f.outlet_id = o.id
        left join feedarticle_feed ff on ff.feeds_id = f.id
        where ff.articles_id = %d
        '''
        self._initDB()
        session = self._session_maker()
        query = template % txto.id
        result = []
        for name in session.query('name').execution_options().from_statement(text(query)).all():
            result.append(name[0])
        session.close()
        txto.outlets = result

    def getSample(self, size = 100, seed = 12345):
        random.seed(seed)
        ids = [i for i in self.getIds()]; random.shuffle(ids)
        id_sample = ids[:size]
        for txto in self.getTexts(id_sample):
            yield txto

    def __iter__(self):
        '''Open a session to the database and iterate over article texts. '''
        self._initDB()
        session = self._session_maker()
        for id, txt, title in session.query("id","text","feedtitle").\
                    execution_options(stream_result=True).\
                    from_statement(text("SELECT id, text, feedtitle FROM feedarticle")).all() :
            txt = Text(id, txt, title=title)
            yield txt
        session.close()

class FeedsetCorpus(FeedsuckerCorpus):
    '''
    Corpus of the text documents in the feedsucker database which belong
    to a specified set of seeds, and are restricted by a date range.
    '''

    query_template = '''
    SELECT %s FROM feedarticle WHERE
        %s
        (id IN (SELECT DISTINCT art.id AS feed_id FROM feedarticle AS art
        JOIN (
        SELECT DISTINCT articles_id, feeds_id FROM feedarticle_feed WHERE feeds_id IN
            ( SELECT id FROM feed WHERE url IN %s )
        ) AS t ON art.id = t.articles_id))
        %s
    '''
    def __init__(self, dbName, feedlist, id = None, uname='rsssucker', pword='rsssucker',
                        startDate=None, endDate=None):
        '''

        :param feedlist: list of string feed urls
        :param id: corpus id
        :param startdate: include only texts after this date
        :param enddate:  include only texts before this date
        Dates are specified as string in 'YYYY-MM-DD hh:mm:ss' format.
        '''
        FeedsuckerCorpus.__init__(self, dbName, uname, pword)
        self.feedlist = feedlist; self.__id = id
        self.startDate, self.endDate = startDate, endDate

    @property
    def id(self):
        if self.__id is not None: return self.__id
        else: return self._dbname+('_feedset[%s]' % self.feedlist.id)

    def __feedSet(self):
        'get set of feed urls for sql queries'
        return '(' + ','.join(["'%s'"%url for url in self.feedlist.urls]) + ')'

    def __queryTemplate(self, randomOrder=False):
        if randomOrder: return \
            'SELECT setseed(0.1);\n'+self.query_template+'\n ORDER BY random()'
        else: return self.query_template

    def __dateCondition(self):
        cond = ''
        if self.startDate:
            cond += ''' (datepublished > '%s' OR
                        (datepublished IS NULL AND datesaved > '%s')) AND ''' \
                    % (self.startDate, self.startDate)
        if self.endDate:
            cond += ''' (datepublished < '%s' OR
                        (datepublished IS NULL AND datesaved < '%s')) AND ''' \
                    % (self.endDate, self.endDate)
        return cond

    def getIds(self):
        'read all ids from the filtered database'
        #RsssuckerCorpus._initDB(self)
        self._initDB()
        session = self._session_maker()
        query = self.__queryTemplate() % ('id' , self.__feedSet(), '')
        for id in session.query('id').execution_options(stream_result=True).\
                    from_statement(text(query)).all() :
            yield id[0]
        session.close()

    def getTexts(self, id_list):
        self._initDB()
        'yield (id, text) pairs for text with specified ids'
        # create list of ids for sql query
        if len(id_list) == 0 : return
        id_str = '('+','.join([str(i) for i in id_list])+')'
        query = self.__queryTemplate() \
                % ('id, text, feedtitle, datesaved, datepublished, url',
                   self.__dateCondition(), self.__feedSet(), 'AND id IN %s' % id_str)
        session = self._session
        for id, txt, title, datesav, datepub, url in \
                session.query('id','text','feedtitle','datesaved', 'datepublished', 'url').\
                execution_options(stream_result=True).from_statement(text(query)).all() :
            txt = Text(id, txt, title=title, date=datesav, url=url,
                        datesaved=datesav, datepublished=datepub)
            yield txt
        session.close()

    def __iter__(self):
        ''' opens a session to the database and iterates over article texts '''
        self._initDB()
        session = self._session_maker()
        query = self.__queryTemplate(True) \
                % ('id, text, feedtitle, datesaved, datepublished, url',
                   self.__dateCondition(), self.__feedSet(), '')
        for id, txt, title, datesav, datepub, url in session.query('id','text','feedtitle',
                                                       'datesaved', 'datepublished', 'url').\
                    execution_options(stream_result=True).from_statement(text(query)).all() :
            txt = Text(id, txt); txt.title = title; txt.date = datesav; txt.url = url
            txt.datesaved = datesav; txt.datepublished = datepub
            yield txt
        session.close()

class IdsetCorpus(FeedsuckerCorpus):
    '''
    Corpus of text documents in a feedsucker database defined by a set of ids.
    '''
    query_template = '''
    SELECT %s FROM feedarticle WHERE id in %s
    '''
    def __init__(self, id, dbName, idSet, uname='rsssucker', pword='rsssucker'):
        FeedsuckerCorpus.__init__(self, dbName, uname, pword, id=id)
        self.idSet = idSet

    def __idSet(self):
        'get set of ids for sql queries'
        return '(' + ','.join(['%d' % id for id in self.idSet]) + ')'

    def __queryTemplate(self, randomOrder=False):
        if randomOrder: return \
            'SELECT setseed(0.1);\n'+self.query_template+'\n ORDER BY random()'
        else: return self.query_template

    def getIds(self):
        'read all ids from the filtered database'
        #RsssuckerCorpus._initDB(self)
        self._initDB()
        session = self._session_maker()
        query = self.__queryTemplate() % ('id' , self.__idSet())
        for id in session.query('id').execution_options(stream_result=True).\
                    from_statement(text(query)).all() :
            yield id[0]
        session.close()

    def __iter__(self):
        " opens a session to the database and iterates over all article texts "
        self._initDB()
        session = self._session_maker()
        query = self.__queryTemplate(True) \
                % ('id, text, feedtitle, datesaved, datepublished, url', self.__idSet())
        #print query
        for id, txt, title, datesav, datepub, url in session.query('id','text','feedtitle',
                                                       'datesaved', 'datepublished', 'url').\
                    execution_options(stream_result=True).from_statement(text(query)).all() :
            txt = Text(id, txt); txt.title = title; txt.date = datesav; txt.url = url
            txt.datesaved = datesav; txt.datepublished = datepub
            yield txt
        session.close()

    def getTexts(self, id_list):
        '''
        yield (id, text) pairs for text with specified ids
        '''
        self._initDB()
        # create list of ids for sql query
        ids = set(i for i in id_list);
        ids.intersection_update(self.idSet)
        if len(ids) == 0 : return
        idStr = '('+','.join([str(i) for i in ids])+')'
        query = self.query_template % ('id, text, feedtitle, datesaved, datepublished, url', self.__idSet())
        query = query + (' AND id IN %s' % idStr)
        session = self._session
        for id, txt, title, datesav, datepub, url in \
                session.query('id','text','feedtitle','datesaved', 'datepublished', 'url').\
                    execution_options(stream_result=True).from_statement(text(query)).all() :
            txt = Text(id, txt); txt.title = title; txt.date = datesav; txt.url = url
            txt.datesaved = datesav; txt.datepublished = datepub
            yield txt
        session.close()

class Feedlist():
    '''
    Encapsulates a list of feed urls, and the id of this feed set.
    '''

    def __init__(self, file):
        '''
        :param file: first line is feed set id, then follows one url per line
        '''
        lines = open(file).readlines()
        self.id = lines[0].strip() # set id is on the first line
        self.urls = set(l.strip() for l in lines[1:] if l.strip() != '')

