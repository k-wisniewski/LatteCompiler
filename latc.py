#!/usr/bin/env python
import getopt
import os
import sys
from parser      import LatteParser
from optimizer   import LatteOptimizer
from typecheck   import LatteSemanticAnalyzer
from jvm_backend import JVM_Backend
from subprocess  import call
from utils       import Logger, VERSION, BLUE, YELLOW, RST


def usage():
    print YELLOW +\
        'latc.py <source_file> [-o <output_file>] [-t <target architecture, eg. jvm, llvm>] ' +\
        '[-v] [-O <optimization level>]' + RST


def greeting():
    print BLUE + 'Latte Compiler v.%s' % VERSION + RST


def main(argv=None):
    greeting()
    if argv is None:
        argv = sys.argv
    try:
        input_file = argv[1]
    except IndexError:
        usage()
        return
    try:
        opts, args = getopt.getopt(argv[2:], 'o:h:t:O:v',
                ['output=', 'help', 'target=', 'optimize=', 'verbose'])
    except getopt.error, msg:
        usage()
        return

    output_file = os.path.splitext(input_file)[0] + '.j'
    target, optimize= 'jvm', 1
    logger = Logger()

    for opt, arg in opts:
        if opt in ('-o', '--output'):
            output_file = arg
        elif opt in ('-h', '--help'):
            usage()
            return 0
        elif opt in ('-t', '--target'):
            target = arg
        elif opt in ('-O', '--optimize'):
            try:
                optimize = int(arg)
            except ValueError:
                logger.error('invalid parameter \'%s\': optimization can be 0 or 1' % arg)
                return
        elif opt in ('-v', '--verbose'):
            logger.verbose = True

    logger.log('Writing to:         $CYAN%s$RST' % output_file)
    logger.log('Target architecure: $CYAN%s$RST' % target)
    logger.log('Optimization level: $CYAN%d (%s)$RST' %\
        (optimize, 'no optimizations' if optimize == 0 else 'simplifying expressions'))
    try:
        with open(input_file) as input_fd:
            parser_instance = LatteParser()
            syntax_tree, parsed = parser_instance.parse(input_fd.read())
            optimizer_instance = LatteOptimizer()
            if syntax_tree and parsed:
                logger.log('Building abstract syntax tree: ....$GREENdone!$RST')
                semantic_analyzer = LatteSemanticAnalyzer(syntax_tree, optimizer_instance)
                if semantic_analyzer.analyze(optimize):
                    logger.log('Performing semantic analysis: .....$GREENdone!$RST')
                    if target == 'jvm':
                        jvm_backend_instance = JVM_Backend(syntax_tree, semantic_analyzer.get_functions())
                        try:
                            with open(output_file, 'w+') as output_fd:
                                output_fd.write(jvm_backend_instance.generate_jvm())
                        except IOError:
                            logger.error('couldn\'t open jvm assembly file for writing')
                        logger.log('Generating jvm assembly file: .....$GREENdone!$RST')
                        with open(os.devnull) as devnull:
                            call(['java', '-jar', 'jasmin.jar', output_file], stdout=devnull)
                        logger.log('Generating class file: ............$GREENdone!$RST')
                else:
                    logger.error('Semantic analysis failed')
            else:
                logger.error('Syntax analysis failed')
    except IOError:
        logger.error('couldn\'t open source file \'%s\'')
if __name__ == '__main__':
    sys.exit(main())
