import sys


MAIN_MANGLING = 65428301
VERSION = '1.0-beta1'


class VariableUndeclared(Exception):
    def __init__(self, msg):
        self.msg = msg


BLACK   = '\033[030;1m'
RED     = '\033[031;1m'
GREEN   = '\033[032;1m'
YELLOW  = '\033[033;1m'
BLUE    = '\033[034;1m'
MAGENTA = '\033[035;1m'
CYAN    = '\033[036;1m'
WHITE   = '\033[037;1m'
RST     = '\033[0m'


class Logger:
    def __init__(self):
        self.verbose = False


    def log(self, what, no_newline=False):
        if self.verbose:
            if no_newline:
                print >> sys.stderr, '\033[032;1m[DEBUG]: \033[0m' + \
                    what.replace('$BLACK', BLACK).replace('$RED', RED).\
                        replace('$GREEN', GREEN).replace('$YELLOW', YELLOW).\
                            replace('$BLUE', BLUE).replace('$MAGENTA', MAGENTA).\
                            replace('$CYAN', CYAN).replace('$WHITE', WHITE).\
                            replace('$RST', RST),
            else:
                print >> sys.stderr, '\033[032;1m[DEBUG]: \033[0m' + \
                    what.replace('$BLACK', BLACK).replace('$RED', RED).\
                        replace('$GREEN', GREEN).replace('$YELLOW', YELLOW).\
                            replace('$BLUE', BLUE).replace('$MAGENTA', MAGENTA).\
                            replace('$CYAN', CYAN).replace('$WHITE', WHITE).\
                            replace('$RST', RST)


    def error(self, what):
        print '\033[031;1m[ERROR]:\033[0m \033[4;1m' + what + '\033[0m'


def get_var(environments, node):
    for env in reversed(environments):
        if node['Name'] in env.keys():
            return env[node['Name']]
    raise VariableUndeclared('Variable %s is undeclared, line: %d, pos: %d - %d' %
            (node['Name'], node['LineNo'], node['StartPos'], node['EndPos']))

