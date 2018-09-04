'''
sota.token
'''

KIND2NAME = {
    261: 'sym',
    262: 'num',
    263: 'str',
    264: 'cmt',
}
for c in xrange(40, 127):
    KIND2NAME[c] = chr(c)

class Token(object):
    '''
    Token
    '''

    def __init__(self, kind, value, line, pos, skip, debug):
        '''
        init
        '''
        self.name = KIND2NAME[kind]
        self.kind = kind
        self.value = value
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
        return 'Token(name=%s kind=%d value=%s line=%d pos=%d skip=%s debug=%d)' % (
            self.name,
            self.kind,
            self.value,
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
