'''
Created on Aug 9, 2014

@author: dam1root
'''

# Interactive console for Croatian_stemmer, reads line by line from stdin
# tokenizes the line and outputs whitespace separated stemmed words on a single line.
# Terminates when 'EXIT' is read 

import Croatian_stemmer
from Croatian_stemmer import transformiraj
from Croatian_stemmer import korjenuj

import sys, re

def stemWord(word):
    return korjenuj(transformiraj(word.lower()))

def stringToUnicode(string):
    return unicode(string, 'utf-8')

def tokenizeAndStem(phrase):
    if not isinstance(phrase, unicode):
        phrase = stringToUnicode(phrase)
    phrase = phrase.strip().lower()
    return ' '.join([ stemWord(w) for w in re.split(r'\s+', phrase) ])

def run():    
    while True:        
        line = sys.stdin.readline().strip()
        if line == "EXIT" : break
        else : 
		tokLine = tokenizeAndStem(line)        		
		print tokLine.encode('utf-8')
		sys.stdout.flush()


