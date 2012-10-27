import re
import sys
import getopt

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def usage():
    print "--input=<file name> to specify input file"
    print "--output=<file name> to specify output file"

def identifier(scanner, token):   return "IDENT", token
def add_operator(scanner, token): return "ADD_OPERATOR", token
def mul_operator(scanner, token): return "MUL_OPERATOR", token
def rel_operator(scanner, token): return "REL_OPERATOR", token
def log_operator(scanner, token): return "LOG_OPERATOR", token
def digit(scanner, token):        return "DIGIT", token
def true(scanner, token):         return "TRUE", None
def false(scanner, token):        return "FALSE", None

def end_stmnt(scanner, token):    return "END_STATEMENT", None
def if_stmt(scanner, token):      return "IF", None
def else_stmt(scanner, token):    return "ELSE", None
def ret_stmt(scanner, token):     return "RETURN", None
def while_stmt(scanner, token):   return "WHILE", None
def assign_stmt(scanner, token):  return "ASSIGN", None
def incr_stmt(scanner, token):    return "INCR", None
def decr_stmt(scanner, token):    return "DECR", None

def type_decl(scanner, token):    return "TYPE", token

def par_l(scanner, token):        return "(", None
def par_r(scanner, token):        return ")", None
def block(scanner, token):        return "BLOCK_START", None
def end_block(scanner, token):    return "BLOCK_END", None

class Lexer:
    def __init__(self, program_code):
        self.tokens, self.remainders = None, None
        self.index = 0
        scanner = re.Scanner([
            (r"\{", block),
            (r"\}", end_block),
            (r"\(", par_l),
            (r"\)", par_r),
            (r"int|string|boolean|void", type_decl),
            (r"true", true),
            (r"false", false),
            (r"\+|\-", add_operator),
            (r"\*|\/|\%", mul_operator),
            (r"\<|\>|\<\=|\>\=|\=\=|\!\=", rel_operator),
            (r"\!|&&|\|\|", log_operator),
            (r"if", if_stmt),
            (r"else", else_stmt),
            (r"while", while_stmt),
            (r"\=", assign_stmt),
            (r"\+\+", incr_stmt),
            (r"\-\-", decr_stmt),
            (r"return", ret_stmt),
            (r"\;", end_stmnt),
            (r"[0-9]+(\.[0-9]+)?", digit),
            (r"[a-zA-Z_]\w*", identifier),
            (r"\s+", None),
            ])
        self.tokens, self.remainder = \
            scanner.scan(self.__preprocess(program_code))
        for i in self.tokens:
            print i

    def __iter__(self):
        return self

    def __preprocess(self, program_code):
        def replacer(match):
            s = match.group(0)
            return "" if s.startswith('/') else s
        pattern = re.compile(
            r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
            re.DOTALL | re.MULTILINE)
        return "".join(re.sub(pattern, replacer, program_code).split())

    def next(self):
        if self.index == len(self.tokens):
            raise StopIteration
        self.index = self.index + 1
        return self.tokens[self.index]

## TEST
def main(argv=None):
    input_file, output_file = None, None
    input_fd, output_fd = None, None

    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "i:o:h", ["input=", "output=", "help"])
        except getopt.error, msg:
            raise Usage(msg)
        if len(opts) != 2:
            usage()
            return 1

        for opt, arg in opts:
            if opt in ("-o", "--output"):
                output_file = arg
            elif opt in ("-i", "--input"):
                input_file = arg
            elif opt in ("-h", "--help"):
                usage()
                return 0

        with open(input_file) as input_fd:
            lexer = Lexer(input_fd.read())
            #for token in lexer:
            #    print token


    except Usage, err:
        print >>sys.stderr, err.msg
        return 2
    #except:
    #    usage()


if __name__ == "__main__":
    sys.exit(main())

