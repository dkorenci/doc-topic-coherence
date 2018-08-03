# -*- coding: utf-8 -*-

import re, codecs
from os import path

from pytopia.corpus.Corpus import Corpus
from pytopia.corpus.text.parse import parseLine

class TextPerLineCorpus(Corpus):
    '''
    Pytopia corpus interface for reading a set of texts from UTF8 file where
    each line contains one text, in format property1=value1, property2=value2, ...
    Last property on each line has to be 'text'
    '''
    # todo solve file position storing, f.tell(), f.seek() do not work for codecs files

    def __init__(self, file, enc='utf-8', id=None):
        self.__file = file; self.__enc = enc
        self.__structsUpdated = False
        self.__ids = set()
        self.__id2pos = {}
        if id: self.id = id
        else: # set id to filename without extension
            self.id = path.splitext(file)[0]

    def getTexts(self, ids):
        self.__buildDataStructs()
        idpos = [(id, self.__id2pos[id]) for id in ids if id in self.__id2pos ]
        idpos.sort(key=lambda pair:pair[1]) # sort by pos
        texts = self.__readTexts([pos for _, pos in idpos]) # read texts off positions
        for i, txto in enumerate(texts): # check that texts have right ids
            assert txto.id == idpos[i][0]
        id2index = { idp[0]:i for i, idp in enumerate(idpos) } # map id -> text/pos index
        return [ (texts[id2index[id]] if id in id2index else None) for id in ids ]

    def __readTexts(self, pos, rawText=False):
        '''
        :param pos: list of positions in the files
        :return: list of texts read off the positions
        '''
        f = codecs.open(self.__file, 'r', self.__enc)
        result = []
        for p in pos:
            f.seek(p)
            line = f.readline()
            if rawText: result.append(line)
            else:
                txto = parseLine(line.strip())
                result.append(txto)
        return result

    def __iter__(self):
        f = codecs.open(self.__file, 'r', self.__enc)
        while True:
            pos = f.tell()
            line = f.readline()
            if line == '': break
            line = line.strip()
            if line == '': continue # ignore empty lines
            txto = parseLine(line)
            self.__updateDataStructs(txto, pos)
            yield txto
        self.__structsUpdated = True
        f.close()

    def testLines(self):
        '''
        For testing, write to file string read from stored text positions.
        :return:
        '''
        f = codecs.open('testLines.txt', 'w', 'utf-8')
        for id_, pos in self.__id2pos.iteritems():
            f.write(id_+'\n')
            f.write(self.__readTexts([pos], rawText=True)[0]+'\n')

    def __buildDataStructs(self):
        '''Read all the texts from the corpus and build data structs.'''
        if self.__structsUpdated: return
        for _ in self: pass

    def __updateDataStructs(self, txto, pos):
        '''
        Update data structures with corpus data.
        :param txto:
        :param pos:
        :return:
        '''
        if self.__structsUpdated: return
        if txto.id in self.__ids: return
        self.__ids.add(txto.id)
        self.__id2pos[txto.id] = pos

    def textIds(self):
        self.__buildDataStructs()
        return list(self.__ids)

def escapeString(s):
    '''
    Escape special chars of the text per line corpus syntax.
    '''
    special = [',', '=']
    for c in special: s = s.replace(c, '\\'+c)
    return s

def formatTextAsLine(txto, properties=None):
    '''
    Transforms pytopia Text object to a string line for the purpose
    of storing the text in a TextPerLineCorpus file.
    :param properties: Text properties to include in the string.
        If None, all the object's attributes not starting with '_' are included.
        'id' and 'text' are always included and mandatory.
    '''
    #todo escaping of = and ,
    props = []
    e = escapeString
    props.append(u'id=%s, ' % e(unicode(txto.id)))
    for prop in dir(txto):
        if not prop.startswith('_') and prop not in ['id', 'text']:
            props.append(u'%s=%s, ' % (e(prop), e(getattr(txto, prop))))
    props.append(u'text=%s' % unicode(txto.text))
    return ''.join(props)

if __name__ == '__main__':
    line = 'id=3, prop1 = some text here, text=and the main text here'
    line = 'id=3, prop1 = some\, text\, here, text=and the main text here'
    #line = 'id=3,prop1=val1,prop2=val2,text=and the main text here'
    line='''id=201384, title=Texas Prisoners Still Face Deadly Heat: Report      \,mj\,\,, url=http://www.huffingtonpost.com/2015/04/03/texas-prisons-heat-deadly_n_7000658.html?utm_hp_ref=politics&ir=Politics, datepublished=2015-04-03 20:45:46, date=2015-04-03 20:53:54.642000, datesaved=2015-04-03 20:53:54.642000, text=Texas Republican gubernatorial candidate Greg Abbott speaks as Lt. Gov. candidate Dan Patrick, right, looks over his shoulder at a campaign event, Monday, Nov. 3, 2014, in Houston. (AP Photo/Pat Sullivan) | ASSOCIATED PRESS  Inmates in Texas prisoners still face lethal heat conditions, one year after those circumstances were first uncovered, a new report found.  "The extreme, suffocating heat in Texas prisons that has claimed the lives of at least 14 inmates since 2007 does not seem to have an end in sight as both Texas and the United States federal government have failed to take action," the report, by the Human Rights Clinic at the University of Texas School of Law, said. "Inmates and guards at [Texas Department of Criminal Justice] prisons are regularly subjected to extremely high temperatures and humidity levels resulting from Texas summertime conditions and the lack of air conditioning and adequate ventilation in TDCJ facilities."  Last year the Human Rights Clinic released a report detailing the conditions it said it found in the state's prisons. That report also noted that, two years prior, an inmate died from organ failure spurred on by what the clinic said were oppressive heat conditions.  "The well-being of staff and offenders is a top priority for the agency and we remain committed to making sure that both are safe during the extreme heat," Hurst said in a statement. "TDCJ takes precautions to help reduce heat–related illnesses such as providing water and ice to staff and offenders in work and housing areas, restricting offender activity during the hottest parts of the day, and training staff to identify those with heat related illnesses and refer them to medical staff for treatment."  Hurst also listed several measures taken by the TDCJ to lower temperatures, including providing fans to inmates, allowing them to wear shorts and providing additional showers for prisoners "when feasible."  But the report said these remedies are inadequate or are not being effectively implemented.  While it's true, for example, that Texas prisons do provide ice, one inmate said the ice is sometimes dirty and filled with mosquitos.  And though staff is supposed to deliver ice to inmates' cells, this isn't always done, the report found.  The report also said providing fans for inmates isn't enough:  Inmates also disputed Hurst's claim that they were offered more showers during the hotter months.  Prisoner Freddie Fountain told the clinic that staff at his unit “absolutely does not allow any such extra showers.”  Ultimately, the report insists, the TDCJ must dramatically increase ventilation and install air conditioners.  Hurst said the price of doing so is too high.  "Although a detailed cost analysis has not been done, retrofitting facilities with air conditioning would be extremely expensive," Hurst said. "It should be noted that medical, psychiatric and geriatric units are air conditioned."  Like Us On Facebook |    Follow Us On Twitter |    Contact The Author '''
    txt = parseLine(line)
    print txt.id
    for att, val in txt: print att, val
    print txt.text