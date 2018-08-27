'''
sota.token
'''

class Token(object):
    '''
    Token
    '''

    def __init__(self, name, value, kind, line, pos, skip, debug):
        '''
        init
        '''
        self.name = name
        self.value = value
        self.kind = kind
        self.line = line
        self.pos = pos
        self.skip = skip
        self.debug = debug

    def to_str(self):
        '''
        to_str
        '''
        return '[%s %s %s:%s]' % (
            self.name,
            self.value,
            self.line,
            self.pos)

    def to_repr(self):
        '''
        to_repr
        '''
        return 'Token(name=%s value=%s kind=%d line=%d pos=%d skip=%s debug=%d)' % (
            self.name,
            self.value,
            self.kind,
            self.line,
            self.pos,
            self.skip,
            self.debug)

    def is_name(self, *names):
        '''
        is_name
        '''
        for name in list(names):
            if name == self.name:
                return True
        return False
