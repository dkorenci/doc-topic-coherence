# -*- coding: utf-8 -*-

'''
Reading and combining stopword lists from txt files.
'''

import codecs, re, os
import unicodedata


class StopwordReader():
    '''
    Remove comments, get stopwords, generate new stopwords based on generation rules.
    '''
    def __init__(self, commentStart = '//', removeAccents = True, verbose = False):
        self.commentStart = commentStart
        self.removeAccents = removeAccents
        self.verbose = verbose

    def readStopwords(self, swfile):
        ':return : a set of stopword strings'
        allSwords = []
        for line in codecs.open(swfile, 'r', encoding='utf-8'):
            swords = self.getStopwords(line)
            if self.removeAccents:
                swords = [ StopwordReader.stripAccents(sw) for sw in swords ]
            allSwords.extend(swords)
            if self.verbose: print ':'.join(swords)
        return set(allSwords)

    # delimiter sequence between stopwords, spaces and optionally one comma
    swDelimiter = re.compile(r'\s*,?\s*')
    def getStopwords(self, line):
        '''
        get all stopwords from the line: remove comments, tokenize,
        and expand stopwords into multiple forms, if applicable'
        :return: list of stopwords, not necessarily unique
        '''
        line = self.removeComment(line).strip()
        if line == '' : return []
        result = []
        for sw in re.split(StopwordReader.swDelimiter, line):
            result.extend(self.expandStopword(sw))
        return result

    def removeComment(self, line):
        'remove all chars from commentStart to the end of string'
        ind = line.find(self.commentStart)
        if ind != -1 : line = line[:ind]
        return line

    @staticmethod
    def stripAccents(s):
        return u''.join(StopwordReader.stripAccent(ch) for ch in s)

    notstrip = u'čćđšž'
    @staticmethod
    def stripAccent(char):
        if char in StopwordReader.notstrip: return char
        # decompose char, remove all accents
        return u''.join(c for c in unicodedata.normalize('NFD', char)
                          if unicodedata.category(c) != 'Mn')

    notstripCD = u'\u030C\u0301\u0304' # (croatian) diacritics not to be stripped
    @staticmethod
    def stripAccentsOld(s):
        # decompose (separate diacritics and letters) unicode, remove all
        # diacritics but those from normal croatian letters
        # the result will be in decomposed form
        decRem = u''.join(c for c in unicodedata.normalize('NFD', s)
                      if unicodedata.category(c) != 'Mn' or c in StopwordReader.notstripCD)
        # compose back (merge diacritics and letters) to unicode
        result = unicodedata.normalize('NFC', decRem)
        return result


    # pattern describing any characters within parentheses
    optionalPart = re.compile(r'\([^\(\)]+\)')
    def expandStopword(self, sw):
        '''
        for stopwords with embedded (.+), produce two stopwords, one with and one without it
        :return: list of stopwords
        '''
        match = re.search(StopwordReader.optionalPart, sw)
        if match is None: return [sw]
        matches = re.findall(StopwordReader.optionalPart, sw)
        if len(matches) > 1: # more than one optional part within '(' ')'
            raise Exception('stopword %s has more than one optional group' % sw)
        sw1 = re.sub(StopwordReader.optionalPart, '', sw) #remove optional part
        # include optional part, remove parentheses
        sw2 = re.sub(StopwordReader.optionalPart, lambda match: match.group(0)[1:-1], sw)
        return [sw1, sw2]

# todo: add class stopword set, enable adding or removing stopwords file by file
def readStopwords(folder, swFiles, nonswFiles = None, verbose = False):
    '''
    get stopword list by reading token from swFiles and nonswFiles from folder,
     and subtracting nonstopwords from stopwords
    '''
    swords = set()
    swr = StopwordReader()
    for fname in swFiles.split():
        sw = swr.readStopwords(os.path.join(folder, fname))
        swords = swords.union(sw)
    if nonswFiles is not None:
        for fname in nonswFiles.split():
            nsw = swr.readStopwords(os.path.join(folder, fname))
            swords = swords.difference(nsw)
    if verbose: print '\n'.join(sw for sw in swords)
    return swords

sw_folder = os.path.join(os.path.dirname(__file__), 'stopword_files')
sw_files = 'cro_stopwords.txt hr_zamjenice.txt'

def croStopwords():
    'get list of croatian stopwords'
    return readStopwords(sw_folder, sw_files)

def testStopwords():
    croStopwords()


