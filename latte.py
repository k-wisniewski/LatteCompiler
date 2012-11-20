import typecheck
import parser
import getopt
import sys

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def usage():
    print "Latte <source_file> -o <output_file>"

def main(argv=None):
    if argv is None:
        argv = sys.argv
    #try:
    input_file = argv[1]
    try:
        opts, args = getopt.getopt(argv[2:], "i:o:h", ["output=", "help"])
    except getopt.error, msg:
        raise Usage(msg)

    for opt, arg in opts:
        if opt in ("-o", "--output"):
            output_file = arg
        elif opt in ("-h", "--help"):
            usage()
            return 0

    with open(input_file) as input_fd:
        parser_instance = parser.LatteParser()
        syntax_tree = parser_instance.parse(input_fd.read())
        if syntax_tree:
            semantic_analyzer = typecheck.LatteSemanticAnalyzer(syntax_tree)
            semantic_analyzer.analyze()

#    except Usage as err:
#        print >> sys.stderr, err.msg
#        return 2
#    except as e:
#        usage(e)
#



if __name__ == "__main__":
    sys.exit(main())
