
class Text(object):
    '''
    Defines interface for Text-like objects, and gives simple implementation.
    'id' (unique id at corpus level) and 'text' (text as string) are
    mandatory attributes, other attributes are text-specific and optional.
    '''

    def __init__(self, id, text, **attributes):
        '''
        Define id, text and a list of arbitrary attributes.
        :param attributes: list of name=value, converted to object attributes
        '''
        self.id = id
        self.text = text
        for attr, val in attributes.iteritems():
            self.__dict__[attr] = val

    def __iter__(self):
        '''
        Iteration over name, value pairs for
        non-standard (id, text) attributes in the text.
        '''
        for key, value in self.__dict__.iteritems():
            if not key.startswith('_'):
                if key != 'id' and key != 'text':
                    yield key, value

def copyText(txt):
    '''
    Create a shallow copy of a Text-like object, as a new Text object with identical attributes.
    '''
    atts = { name:val for name, val in txt }
    return Text(txt.id, txt.text, **atts)