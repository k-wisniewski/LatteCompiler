#!/usr/bin/env python
import getopt
import os
import sys
from subprocess       import call
from src.parser       import LatteParser
from src.optimizer    import LatteOptimizer
from src.typecheck    import LatteSemanticAnalyzer
from src.jvm_backend  import JVM_Backend
from src.llvm_backend import LLVM_Backend
from shared.utils     import Logger, VERSION, BLUE, YELLOW, RST, RED


def usage():
    print YELLOW +\
        'latc.py <source_file> [-o <output_file>] [-t <target architecture jvm, llvm, both>] ' +\
        '[-v] [-O <optimization level>] [-j <jasmin jar file>]' + RST


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        input_file = argv[1]
    except IndexError:
        usage()
        return -1
    try:
        opts, args = getopt.getopt(argv[2:], 'o:h:t:j:O:v',
                ['output=', 'help', 'target=', 'jasmin=', 'optimize=', 'verbose'])
    except getopt.error, msg:
        usage()
        return -1

    output_file = os.path.splitext(input_file)[0]
    target, optimize, jasmin = 'both', 1, 'lib/jasmin.jar'
    logger = Logger()

    for opt, arg in opts:
        if opt in ('-o', '--output'):
            output_file = arg
        elif opt in ('-h', '--help'):
            usage()
            return 0
        elif opt in ('-t', '--target'):
            target = arg
        elif opt in ('-j', '--jasmin'):
            jasmin = arg
        elif opt in ('-O', '--optimize'):
            try:
                optimize = int(arg)
            except ValueError:
                logger.error('invalid parameter \'%s\': optimization can be 0 or 1' % arg)
                return
        elif opt in ('-v', '--verbose'):
            logger.verbose = True

    logger.log('$BLUELatte Compiler v.%s$RST' % VERSION)
    logger.log('Writing to:         $CYAN%s$RST' % output_file)
    logger.log('Target architecure: $CYAN%s$RST' % target)
    logger.log('Optimization level: $CYAN%d (%s)$RST' %\
        (optimize, 'no optimizations' if optimize == 0 else 'simplifying expressions'))
    if target in ('jvm', 'both'):
        logger.log('Jasmin .jar file:   $CYAN%s$RST' % jasmin)
    try:
        with open(input_file) as input_fd:
            parser_instance = LatteParser(logger)
            syntax_tree, parsed = parser_instance.parse(input_fd.read())
            optimizer_instance = LatteOptimizer()
            if syntax_tree and parsed:
                logger.log('Building abstract syntax tree: ....$GREENdone!$RST')
            #    if target in ('jvm', 'both'):
            #        semantic_analyzer = LatteSemanticAnalyzer(syntax_tree, optimizer_instance, 'jvm', logger)
            #        if semantic_analyzer.analyze(optimize):
            #            logger.log('Performing semantic analysis: .....$GREENdone!$RST')
            #            jvm_backend_instance = JVM_Backend(syntax_tree,
            #                    semantic_analyzer.get_functions(),
            #                    (os.path.basename(os.path.splitext(input_file)[0]).capitalize()))
            #            try:
            #                with open(output_file, 'w+') as output_fd:
            #                    output_fd.write(jvm_backend_instance.generate_jvm())
            #            except IOError:
            #                logger.error('couldn\'t open jvm assembly file for writing')
            #            logger.log('Generating jvm assembly file: .....$GREENdone!$RST', True)
            #            with open(os.devnull) as devnull:
            #                arg_list = ['java', '-jar', jasmin, '-d',
            #                    os.path.split(output_file)[0], output_file]
            #                if optimize == 0:
            #                    arg_list.append('-g')
            #                print >> sys.stderr, RED,
            #                call(arg_list, stdout=devnull)
            #                print >> sys.stderr, RST
            #            logger.log('Generating class file: ............$GREENdone!$RST')
            #            logger.accept()
            #            return 0
            #    el
                if target in ('llvm', 'both'):
                    semantic_analyzer = LatteSemanticAnalyzer(syntax_tree, optimizer_instance, 'llvm', logger)
                    if semantic_analyzer.analyze(optimize):
                        logger.log('Performing semantic analysis: .....$GREENdone!$RST')
                        llvm_backend_instance = LLVM_Backend(syntax_tree, semantic_analyzer.get_functions(),
                                semantic_analyzer.get_class_meta(),
                                os.path.basename(os.path.splitext(input_file)[0]).capitalize())
                        llvm_ir = llvm_backend_instance.generate_llvm()
                        try:
                            with open(output_file + '.ll', 'w+') as output_fd:
                                output_fd.write(llvm_ir)
                        except IOError:
                            logger.error('couldn\'t open llvm assembly file for writing')
                        logger.accept()
                    else:
                        return -1
                else:
                    logger.error('Semantic analysis failed')
                    return -1
            else:
                logger.error('Syntax analysis failed')
                return -1
    except IOError:
        logger.error('couldn\'t open source file \'%s\'' % input_file)
        return -1
if __name__ == '__main__':
    sys.exit(main())
