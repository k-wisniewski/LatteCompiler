import sys


MAIN_MANGLING = 65428301
VERSION = '1.0'


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


PRIMITIVES = ('int', 'boolean', 'string', 'void', 'null')


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
        if self.verbose:
            print '\033[031;1m[ERROR]:\033[0m \033[4;1m' + what + '\033[0m'
        else:
            print "ERROR:"
            print what


    def accept(self):
        if not self.verbose:
            print "OK"


class InvalidExpression(Exception):
    def __init__(self, msg):
        self.msg = msg


class InvalidStatementType(Exception):
    def __init__(self, msg):
        self.msg = msg


def get_var(environments, node, class_envs=None, current_class=None):
    for env in reversed(environments):
        if node['Name'] in env:
            return env[node['Name']]

    if class_envs and current_class:
        class_name = current_class['Name']
        if node['Name'] in class_envs[class_name].attributes:
            return class_envs[class_name].attributes[node['Name']]
        while class_envs[class_name].extends:
            if node['Name'] in class_envs[class_name].attributes:
                return class_envs[class_name].attributes[node['Name']]
            class_name = class_envs[class_name].extends

    raise VariableUndeclared('Variable %s is undeclared, line: %d, pos: %d - %d' %
            (node['Name'], node['LineNo'], node['StartPos'], node['EndPos']))


def is_member(member_name, class_envs, class_name, method=False):
    test = lambda class_name: member_name in class_envs[class_name].methods\
        if method else member_name in class_envs[class_name].attributes
    while True:
        if test(class_name):
            return True
        class_name = class_envs[class_name].extends
        if not class_name:
            break
    return False


def get_member(member_name, class_envs, class_name, method=False):
    test = lambda class_name: member_name in class_envs[class_name].methods\
        if method else member_name in class_envs[class_name].attributes
    to_be_returned = lambda class_name: class_envs[class_name].methods[member_name] if member_name else\
            class_envs[class_name].attributes[member_name]
    while True:
        if test(class_name):
            return to_be_returned(class_name)
        class_name = class_envs[class_name].extends
        if not class_name:
            break
    return None


def get_function(node, functions, class_envs=None, current_class=None):
    if current_class and class_envs and is_member(node['Name'], class_envs, current_class['Name'], True):
        if get_member(node['Name'], class_envs, current_class['Name'], True):
            return method
    elif functions and node['Name'] in functions:
        return functions[node['Name']]
    raise InvalidExpression('function %s undeclared, line: %d, pos: %d - %d' %\
            (node['Name'], node['LineNo'], node['StartPos'], node['EndPos']))


def is_a(type1, meta_type1, type2, meta_type2, class_envs):
    if type1 != 'null' and meta_type1 != meta_type2:
        return False
    if type1 != 'null' and meta_type1 in ('Primitive', 'Array'):
        return type1 == type2
    if type1 != 'null' and meta_type2 == 'Class':
        class_name = type1
        while class_name:
            if class_name == type2:
                return True
            class_name = class_envs[class_name].extends
    if type1 == 'null' and meta_type2 == 'Class':
        return True
    return False





