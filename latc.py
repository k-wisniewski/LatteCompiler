import typecheck
import optimizer
import parser
import getopt
import jvm_backend
import sys

def usage():
    print "Latte <source_file> -o <output_file> -t <target architecture, eg. jvm, llvm>"

def main(argv=None):
    if argv is None:
        argv = sys.argv
    #try:
    input_file = argv[1]
    try:
        opts, args = getopt.getopt(argv[2:], "o:h:t", ["output=", "help", "target="])
    except getopt.error, msg:
        usage()
        return

    for opt, arg in opts:
        if opt in ("-o", "--output"):
            output_file = arg
        elif opt in ("-h", "--help"):
            usage()
            return 0
        elif opt in ("-t", "--target"):
            target = arg

    print "out %s"% output_file
    print "target %s"% target
    with open(input_file) as input_fd:
        parser_instance = parser.LatteParser()
        syntax_tree = parser_instance.parse(input_fd.read())
        optimizer_instance = optimizer.LatteOptimizer()
        if syntax_tree:
            semantic_analyzer = typecheck.LatteSemanticAnalyzer(syntax_tree, optimizer_instance)
            semantic_analyzer.analyze()
            if target == "jvm":
                jvm_backend_instance = jvm_backend.JVM_Backend(syntax_tree)
                with open(output_file, "w+") as output_fd:
                    output_fd.write(jvm_backend_instance.generate_jvm())
                #os.execlp("java", "java", "-jar", "jasmin.jar", output_file)


if __name__ == "__main__":
    sys.exit(main())