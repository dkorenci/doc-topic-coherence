class DuplicateTextFilter():
    '''
    Filters duplicate texts using hash functions.
    This filter compares a text with texts already filtered so order of filtering matters.
    If it is initialized with corpus only id's are stored and texts are
    fetched from corpus when neccessary, to conserve space.
    '''
    def __init__(self, corpus = None):
        '''
        :param corpus: If not none, it is assumed that all filtered Text objects
         are from the corpus and full texts can be fetched by id,
         so the corpus will be used as a text store.
        '''
        self.corpus = corpus
        self.__init_data()
        self.id = 'hashing_duplicate_text_filter'

    def __init_data(self):
        self.hash2texts = {}
        self.hashClashes = 0
        self.fetches = 0
        self.duplicates = 0

    def __getstate__(self):
        return self.corpus

    def __setstate__(self, state):
        self.corpus = state
        self.__init_data()

    def __textDuplicate(self, txto, addNew = True):
        '''check if Text object with the same text but different id exists'''
        h = hash(txto.text)
        if h in self.hash2texts :
            self.hashClashes += 1
            if txto.id in [ txtid.id for txtid in self.hash2texts[h] ] :
                return False # same text already stored
            else:
                for txtid in self.hash2texts[h]:
                    # fetch from database if corpus exists
                    if txtid.text is None and self.corpus is not None:
                        result = self.corpus.getText(txtid.id)
                        self.fetches += 1
                        if result is None: txtid.text = None
                        else: txtid.text = result.text
                    if txtid.text == txto.text:
                        #print 'duplication: old %s, new %s' % (str(txtid.id), str(txto.id))
                        return True #duplicate text
                if addNew:
                    if self.corpus is None: txtid = TxtId(txto.id, txto.text)
                    else: txtid = TxtId(txto.id, None)
                    self.hash2texts[h].append(txtid)
                return False
        elif addNew:
            if self.corpus is None: txtid = TxtId(txto.id, txto.text)
            else: txtid = TxtId(txto.id, None)
            self.hash2texts[h] = [ txtid ]

    def __call__(self, txtobj):
        if self.__textDuplicate(txtobj):
            self.duplicates += 1
            #print 'duplicate: ' + txtobj.title
            return True
        else: return False

class TxtId():
    def __init__(self, id, txt): self.text = txt; self.id = id
