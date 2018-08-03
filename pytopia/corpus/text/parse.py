'''
Tools for parsing strings into Text objects.
'''

from pytopia.corpus.Text import Text

import re

def parseLine(line):
    '''
    Parse a string line and return Text object
    'text' property is mandatory and must be last
    :param line: property1=value1, property2=value2, ...
    :return: Text object with properties and their values matching parsed properties.
    '''
    propertyRe = re.compile(r'\s*([a-zA-Z]\w*)\s*=')
    valueRe = re.compile(r'([^,]?(\\,)?)+,(?!,)')
    props = {};
    pos = 0;
    id_ = None
    while pos < len(line):
        # print pos, '[%s]'%line[pos]
        pmatch = propertyRe.match(line, pos)
        if pmatch is not None:
            pos = pmatch.end(0)
            name = line[pmatch.start(1): pmatch.end(1)];
            # print 'full match: [%s]' % line[pmatch.start(0): pmatch.end(0)]
            if name == 'text':
                text = line[pmatch.end(0):]
                return Text(id_, text, **props)
            vmatch = valueRe.match(line, pos);
            if vmatch is None:
                raise Exception('property %s does not have value' % name)
            else:
                # pos = vmatch.end(0)+1 # skip the comma
                pos = vmatch.end(0)
                value = processValue(line[vmatch.start(0): vmatch.end(0) - 1])
                # print name, value
            # process propery, value pair
            if name == 'id': id_ = value
            else: props[name] = value
        else:
            break
    raise Exception('there must be a "text" property')

def processValue(val):
    '''Strip and de-escape commas (\,)'''
    return val.strip().replace('\,', ',')
