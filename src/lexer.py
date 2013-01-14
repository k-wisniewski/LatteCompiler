import ply.lex as lex
import sys

class LatteLexer():
    tokens = [
        'COMMENT',
        'NUM',
        'ID',
        'PAR_L',
        'PAR_R',
        'NEW',
        'SUBSCRIPT_L',
        'SUBSCRIPT_R',
        'ARRAY_TYPE_IND',
        'COMMA',
        'DOT',
        'BR_L',
        'BR_R',
        'END_S',
        'ASSIGN',
        'INC',
        'DEC',
        'MINUS',
        'NOT',
        'AND',
        'OR',
        'PLUS',
        'TIMES',
        'DIV',
        'MOD',
        'LESS',
        'LEQ',
        'GT',
        'GEQ',
        'EQ',
        'NEQ',
        'BOOL',
        'ELSE',
        'FALSE',
        'IF',
        'INT',
        'RET',
        'STRING',
        'TRUE',
        'VOID',
        'WHILE',
        'FOR',
        'FOR_COLON',
        'LITSTR',
        'CLASS',
        'CAST',
        'NULL',
        'EXTENDS'
    ]

    reserved = {
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'for' : 'FOR',
        'return': 'RET',
        'new': 'NEW',
        'boolean': 'BOOL',
        'int': 'INT',
        'string': 'STRING',
        'void': 'VOID',
        'true': 'TRUE',
        'false': 'FALSE',
        'class': 'CLASS',
        'cast': 'CAST',
        'null': 'NULL',
        'extends': 'EXTENDS'
    }

    t_PAR_L = r'\('
    t_PAR_R = r'\)'
    t_ARRAY_TYPE_IND = r'\[\]'
    t_SUBSCRIPT_L = r'\['
    t_SUBSCRIPT_R = r'\]'
    t_COMMA = r'\,'
    t_BR_L = r'\{'
    t_BR_R = r'\}'
    t_DOT = r'\.'
    t_FOR_COLON = r':'
    t_END_S = r'\;'
    t_ASSIGN = r'\='
    t_INC = r'\+\+'
    t_DEC = r'--'
    t_MINUS = r'-'
    t_NOT = r'\!'
    t_AND = r'&&'
    t_OR = r'\|\|'
    t_PLUS = r'\+'
    t_TIMES = r'\*'
    t_DIV = r'\/'
    t_MOD = r'\%'
    t_LESS = r'\<'
    t_LEQ = r'\<\='
    t_GT = r'\>'
    t_GEQ = r'\>\='
    t_EQ = r'\=\='
    t_NEQ = r'\!\='


    def t_COMMENT(self, t):
        r'(/\*(.|\n)*?\*/)|((//|\#).*)'
        t.lineno += t.value.count('\n')

    def t_LITSTR(self, t):
        r'\"(.|\n)*?\"'
        t.lineno += t.value.count('\n')
        return t

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value,'ID')
        return t

    def t_NUM(self, t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            print >> sys.stderr, "Integer value too large %d, line: %d" %(t.value, t.lexer.lineno)
            t.value = 0
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    t_ignore  = ' \t'

    def t_error(self, t):
        print >> sys.stderr, "Illegal character '%s' at line: %d" % (t.value[0], t.lexer.lineno)
        t.lexer.skip(1)

    def build(self, **kwargs):
        # Build the lexer
        self.lexer = lex.lex(module=self, **kwargs)
        return self.lexer

if __name__ == "__main__":
    lexer = LatteLexer().build()
    fd = open(sys.argv[1])
    lexer.input(fd.read())
    while True:
        tok = lexer.token()
        if not tok:
            break
        print tok
