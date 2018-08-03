import logging
from logging import INFO, DEBUG, WARNING, ERROR, CRITICAL, Filter
from time import clock
import datetime
import os, re
from os import path

rootLoggerSetUp = False

def setupRootLogger(rootFolder=None, logFolder='pylog', debug=False, filterPatterns=None):
    '''
    Setup root logger to output messages to timestamped  utf8 txt log file
    inside rootFolder/logFolder. Setup log message format.
    :param rootFolder: folder where the logFolder will be created (default current folder)
    :param logFolder: name of the folder for log files
    :param debug: create separate debug message handler/file
    :param filterPatterns: list, filter all loggers with name containing one of these regex strings
    :return:
    '''
    global rootLoggerSetUp
    rootlog = logging.getLogger()
    rootlog.setLevel(logging.DEBUG)
    now = datetime.datetime.now().strftime('%d.%m.%Y-%H:%M:%S')
    fname = 'log[%s].txt'%now
    folder = path.join(rootFolder, logFolder) if rootFolder else logFolder
    if not path.exists(folder): os.mkdir(folder)
    rootHandler = logging.FileHandler(path.join(folder,fname), encoding='UTF-8')
    if filterPatterns:
        rootHandler.addFilter(RegexNameFilter(filterPatterns))
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s:\n  %(message)s',
                '%d.%m.%Y-%H:%M:%S')
    rootHandler.setFormatter(formatter)
    rootlog.addHandler(rootHandler)
    if debug:
        fname = 'log[%s]_DEBUG.txt' % now
        handler = logging.FileHandler(path.join(folder,fname), encoding='UTF-8')
        handler.addFilter(LevelRangeFilter(DEBUG, DEBUG))
        rootHandler.addFilter(LevelRangeFilter(INFO, CRITICAL))
        rootlog.addHandler(handler)
    rootLoggerSetUp = True
    return rootlog

def createLogger(name, level=logging.DEBUG):
    '''
    Create logger with specifed name and level.
    Default settings are used - delegating all log messages to root logger.
    '''
    global rootLoggerSetUp
    if not rootLoggerSetUp: setupRootLogger()
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger

class LevelRangeFilter():
    '''Filter out log records with level not between two specified levels.'''

    def __init__(self, minLevel, maxLevel):
        self.min, self.max = minLevel, maxLevel

    def filter(self, record):
        if  self.min <= record.levelno <= self.max: return 1
        else: return 0

class RegexNameFilter():
    '''Filter out log records originating from log with name that matches patterns.'''

    def __init__(self, pattStrings):
        '''
        :param pattStrings: list of string regular expressions
        '''
        self.patterns = [re.compile(p) for p in pattStrings]

    def filter(self, record):
        name = record.name
        for patt in self.patterns:
            if patt.search(name): return 0
        return 1