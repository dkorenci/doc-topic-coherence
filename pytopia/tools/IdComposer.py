import types
import inspect

class IdComposer(object):
    '''
    Creates readable string id of an object based on
    a set of object attributes that define its identity.
    '''

    def __init__(self, attributes=None, class_=None):
        '''
        :param attributes: list of attribute names, if None extract from dir()
        :param class_: object 'class' ie category descriptor,
            if None use the __class__ of the object.
        '''
        self.__class = class_ if class_ else self.__class__.__name__
        self.__atts = attributes if attributes else\
                        [att for att in dir(self) if self.__validAttribute(att)]
        self.__id = None

    def __getstate__(self):
        return self.__class, self.__atts, \
               {att: getattr(self, att) for att in self.__atts}, \
               self.__id

    def __setstate__(self, state):
        self.__class, self.__atts, attVals, self.__id = state
        for att in self.__atts: setattr(self, att, attVals[att])

    def __validAttribute(self, att):
        '''
        True if att is valid name for an attribute identifying an object
        '''
        if att.startswith('_'): return False
        if att == 'id' or att == 'setId' or att == 'sid': return False
        if inspect.ismethod(getattr(self, att)): return False
        return True

    @property
    def id(self):
        '''Build id from class name and specified attributes'''
        if self.__id is not None: return self.__id
        else: return self.__structuralId()

    @id.setter
    def id(self, id_):
        '''
        Sets user-defined id that becomes the object's id,
        overriding the structural id.
        If renamed, change the name in '__validAttribute' method.
        '''
        self.__id = id_

    @property
    def sid(self):
        '''
        'structural id' - skip user-assigned id and create id from object attributes.
        If renamed, change the name in '__validAttribute' method.
        '''
        return self.__structuralId()

    def __structuralId(self):
        '''Build id from class name and attributes defining the objects identity'''
        id_ = u'%s' % self.__class + \
              u''.join(self.__attributeId(att) for att in sorted(self.__atts))
        return id_

    def __attributeId(self, att):
        '''
        Creates string representing the specified attribute and its value.
        :param att: attribute name
        '''
        if not hasattr(self, att): return u''
        val = getattr(self, att)
        if val is None: return u''
        # format attribute value depending on its type and attributes
        # create string formatting template for the value depending on its type
        # todo extract value formatting to a separate method
        if isinstance(val, float): valtemp = '%g'
        else: valtemp = '%s'
        template = u'_%s' % att + u'['+valtemp+']' # template to format value
        # if 'id' attribute exists, use it
        if hasattr(val, 'id'): return template % val.id
        # if function, use its name
        if isinstance(val, types.FunctionType):
            return template % str(val.__name__)
        # else use str()
        if isinstance(val, float): return template % val
        else: return template % str(val)

def createId(prefix, **params):
    '''Shorthand for creating an id constructed from param names and values,
    using IdComposer, for clients that have no need for working
    with IdComposer directly.
    '''
    if 'id' in params: raise Exception('id is not an allowed param')
    class Id(IdComposer):
        def __init__(self):
            for name, val in params:
                setattr(self, name, val)
            IdComposer.__init__(self, class_=prefix)
    return Id().id

def deduceId(obj):
    ''' Return obj.id if .id exists, else deduce an approximation for id,
            ie name of the class or function. '''
    import types
    if obj == None: return None
    if hasattr(obj, 'id'): return obj.id
    else:
        if isinstance(obj, types.FunctionType): return obj.__name__
        elif isinstance(obj, types.ClassType): return obj.__name__
        elif isinstance(obj, types.ObjectType): return obj.__class__.__name__
        else: return str(obj)
