#-*-coding:utf-8-*-

import re

from cronlp.span.base import Span

class RegexTokenizer:
    '''
    Tokenization based on regex. Tokenizer is initialized with
    a list of named unicode regexes, each describing one token type.
    '''

    def __init__(self, wordTypes, wspaceTypes, nonregex='other', remove = None, **regexes):
        '''
        :param nonregex: name for a token type not covered by regexes
        :param wordType: when returning string only word string tokens, filter Spans by this type
        :param regexes: map of token type name -> regex
        :param remove: if None, a list of regexes to remove form string before tokenizing
        '''
        self.regexes = regexes
        self.nonregexName = nonregex
        self.wordTypes = wordTypes
        self.wspaceTypes = wspaceTypes
        self.remove = remove

    def createMasterRegex(self):
        'create regex with containing all the type regexes, each in different named group'
        mrstr = u'|'.join( u'(?P<%s>%s)' % (name, self.regexes[name]) for name in self.regexes )
        self.masterRegex = re.compile(mrstr, re.UNICODE)

    def tokenize(self, text):
        '''
        Mark spans of text corresponding to regex groups.
        :param text:
        :return:
        '''
        self.pos = 0 # current position in text
        self.result = []
        self.text = text
        self.__remove()
        self.createMasterRegex()
        # start of a sequence not covered by any regex,
        # if not None indicates such a sequence is 'open'
        self.nonregexStart = None
        while self.pos < len(self.text):
            match = self.masterRegex.match(self.text, pos = self.pos)
            if match is not None: # word or ws matched
                self.closeNonregex()
                matchDict = match.groupdict() # regex (group) name -> matched text
                matchedName = None
                for name in matchDict:
                    if matchDict[name] is not None:
                        if matchedName is None: matchedName = name
                        else: raise Exception('More than one regex match: %s %s, at position %s'
                                              %(matchedName, name, self.text[match.start(0):match.end(0)]) )
                assert matchedName is not None
                self.result.append(Span(match.start(0), match.end(0), self.text, matchedName))
                self.pos = match.end(0)
                continue
            if self.nonregexStart is None: self.nonregexStart = self.pos
            self.pos += 1
        self.closeNonregex()
        # detach data from instance and return
        result = self.result
        self.result = None
        return result

    def __remove(self):
        if self.remove is None: return
        for remreg in self.remove:
            patt = re.compile(remreg, re.UNICODE)
            self.text = patt.sub(u'', self.text)

    def wordStringTokens(self, text, lowercase = False):
        return [ sp.covered().lower() if lowercase else sp.covered()
                    for sp in self.tokenize(text) if sp.type in self.wordTypes ]

    def closeNonregex(self):
        'if open, close nonword sequence at current position and add it to result'
        if self.nonregexStart is not None:
            self.result.append(Span(self.nonregexStart, self.pos, self.text, self.nonregexName))
            self.nonregexStart = None





