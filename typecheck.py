# TODO: Check if function always returns

import sys

class InvalidExpression(Exception):
    def __init__(self, msg):
        self.msg = msg


class InvalidStatementType(Exception):
    def __init__(self, msg):
        self.msg = msg


class VariableUndeclared(Exception):
    def __init__(self, msg):
        self.msg = msg


class LatteSemanticAnalyzer:

    def __load_functions(self):
        main = None
        for function in self.syntax_tree:
            if not function:
                continue
            if function['Name'] in self.functions.keys():
                self.errors.append('ERROR: function %s already defined at line %d, \
                        redefined at line: %d' % (function['Name'], \
                        self.functions['Name']['LineNo'], function['LineNo']))
                continue
            self.functions[function['Name']] = function
            if function['Name'] == 'main':
                main = function
        if not main:
            self.errors.append("ERROR: didn't encounter main function")
            return
        if main['LatteType']['TypeName'] != 'int':
            self.errors.append('ERROR: in declaration of function main:\n\
                    main must return value of type int, line: %d' %
                    main['LineNo'])
            return
        # load built-ins:
        self.functions['printInt'] = {'Type': 'FunDecl', 'LineNo': -1, 'Name': 'printInt',
                'ListArg': [{'Name': 'x', 'LatteType': {'TypeName': 'int', 'LineNo': -1, 'StartPos': -1, 'EndPos': -1},
                    'StartPos': -1, 'EndPos': -1}],
            'Body': [], 'LatteType': {'TypeName': 'void', 'LineNo': -1, 'StartPos': -1, 'EndPos': -1}}
        self.functions['printString'] = {'Type': 'FunDecl', 'LineNo': -1, 'Name': 'printString',
                'ListArg': [{'Name': 'x', 'LatteType': {'TypeName': 'string', 'LineNo': -1, 'StartPos': -1, 'EndPos': -1},
                    'StartPos': -1, 'EndPos': -1}],
            'Body': [], 'LatteType': {'TypeName': 'void', 'LineNo': -1, 'StartPos': -1, 'EndPos': -1}}
        self.functions['printBool'] = {'Type': 'FunDecl', 'LineNo': -1, 'Name': 'printBool',
                'ListArg': [{'Name': 'x', 'LatteType': {'TypeName': 'boolean', 'LineNo': -1, 'StartPos': -1, 'EndPos': -1},
                    'StartPos': -1, 'EndPos': -1}],
            'Body': [], 'LatteType': {'TypeName': 'void', 'LineNo': -1, 'StartPos': -1, 'EndPos': -1}}
        self.functions['readInt'] = {'Type': 'FunDecl', 'LineNo': -1, 'Name': 'readInt',
                'ListArg': [],'Body': [], 'LatteType': {'TypeName': 'int', 'LineNo': -1, 'StartPos': -1, 'EndPos': -1}}
        self.functions['readString'] = {'Type': 'FunDecl', 'LineNo': -1, 'Name': 'readString',
                'ListArg': [],'Body': [], 'LatteType': {'TypeName': 'string', 'LineNo': -1, 'StartPos': -1, 'EndPos': -1}}
        self.functions['readBool'] = {'Type': 'FunDecl', 'LineNo': -1, 'Name': 'readBool',
                'ListArg': [],'Body': [], 'LatteType': {'TypeName': 'boolean', 'LineNo': -1, 'StartPos': -1, 'EndPos': -1}}


    def __push_env(self, function = None):
        self.environments.append({})
        if function:
            for param in function['ListArg']:
                if param['Name'] in self.environments[-1].keys():
                    self.errors.append('ERROR: repeated argument name %s, in declaration of %s, line: %d, pos: %d - %d' %\
                        (param['Name'], function['Name'], function['LineNo'], function['StartPos'], function['EndPos']))
                    continue
                self.environments[-1][param['Name']] = param

    def __get_var(self, node):
        for env in reversed(self.environments):
            if node['Name'] in env.keys():
                return env[node['Name']]
        raise VariableUndeclared('Variable %s is undeclared, line: %d, pos: %d - %d' %
                (node['Name'], node['LineNo'], node['StartPos'], node['EndPos']))


    def __pop_env(self):
        self.environments.pop()

    def __eval_expression_type_unary(self, expression):
        arg_type = self.__eval_expression_type(expression['Arg'])
        if expression['Op']['Op'] == '!' and\
                arg_type == 'boolean':
            return 'boolean'
        elif expression['Op']['Op'] == '-' and\
                arg_type == 'int':
            return 'int'
        elif expression['Op']['Op'] == '!':
            raise InvalidExpression('ERROR: applying operator \'!\' to non-boolean value of type %s, line: %d, pos: %d - %d' % \
                    (arg_type, expression['LineNo'], expression['StartPos'], expression['EndPos']))
        elif expression['Op']['Op'] == '-':
            raise InvalidExpression('ERROR: applying operator \'-\' to non-integer value of type %s, line: %d, pos: %d - %d' %\
                    (arg_type, expression['LineNo'], expression['StartPos'], expression['EndPos']))

    def __eval_expression_type_binary(self, expression):
        left_type = self.__eval_expression_type(expression['Left'])
        right_type = self.__eval_expression_type(expression['Right'])
        if expression['Op'] == '||' or expression['Op'] == '&&':
            if left_type != 'boolean' or right_type != 'boolean':
                raise InvalidExpression('ERROR: operator \'%s\' applied to non-boolean\
expressions, line: %d, pos: %d - %d' % (expression['Op'],\
                        expression['LineNo'], expression['Left']['StartPos'], expression['Right']['EndPos']))
            return 'boolean'
        elif expression['Op']['MetaType'] == 'RelOp':
            if left_type not in ['int', 'boolean'] or\
                    right_type not in ['int', 'boolean']:
                        raise InvalidExpression('ERROR: relational operator %s applied to invalid argument types:\n\
expected int or boolean - got %s and %s, line: %d, pos: %d - %d' %\
                                (expression['Op']['Op'], left_type, right_type, expression['LineNo'],\
                                expression['Left']['StartPos'], expression['Right']['EndPos']))
            return 'boolean'
        elif expression['Op']['MetaType'] == 'ArithmOp' and expression['Op']['Op'] != '+':
            if left_type != 'int' or right_type != 'int':
                raise InvalidExpression('ERROR: arithmetic operator %s applied to invalid argument types:\n\
expected expression of type \'int\', got %s and %s, line: %d, pos: %d - %d' %\
                        (expression['Op']['Op'], left_type, right_type, expression['LineNo'],
                            expression['Left']['StartPos'], expression['Right']['EndPos']))
            return 'int'
        elif expression['Op']['Op'] == '+':
            if left_type not in ['int', 'string'] or right_type not in ['int', 'string'] or left_type != right_type:
                raise InvalidExpression('ERROR: arithmetic operator %s applied to invalid argument types:\n\
expected expression of type \'int\' or \'string\', got %s and %s, line: %d, pos: %d - %d' %\
                        (expression['Op']['Op'], left_type, right_type, expression['LineNo'],
                            expression['Left']['StartPos'], expression['Right']['EndPos']))
            return left_type


    def __eval_expression_type_funcall(self, expression):
        if expression['Name'] not in self.functions.keys():
            raise InvalidExpression('ERROR: function %s undeclared, line: %d, pos: %d - %d' %\
                    (expression['Name'], expression['LineNo'], expression['StartPos'], expression['EndPos']))
        function = self.functions[expression['Name']]
        if len(function['ListArg']) != len(expression['ListArg']):
            raise InvalidExpression('ERROR: invalid number of arguments provided to function %s: \
expected: %d, got: %d, line: %d, pos: %d - %d' %\
                            (function['Name'], len(function['ListArg']), len(expression['ListArg']),\
                                expression['LineNo'], expression['StartPos'], expression['EndPos']))
        for arg_expected, arg_provided in zip(function['ListArg'], expression['ListArg']):
            expr_type = self.__eval_expression_type(arg_provided)
            if expr_type != arg_expected['LatteType']['TypeName']:
                raise InvalidExpression('ERROR: in a call to function %s: expected: %s, got: %s, \
line: %d, pos %d - %d' % (function['Name'], arg_expected['LatteType']['TypeName'],
                            expr_type, expression['LineNo'], expression['StartPos'], expression['EndPos']))
        return function['LatteType']['TypeName']

    def __eval_expression_type(self, expression):
        if expression['Type'] == 'NumLiteral':
            return 'int'
        elif expression['Type'] == 'BoolLiteral':
            return 'boolean'
        elif expression['Type'] == 'StrLiteral':
            return 'string'
        elif expression['Type'] == 'UnaryOp':
            return self.__eval_expression_type_unary(expression)
        elif expression['Type'] == 'BinaryOp':
            return self.__eval_expression_type_binary(expression)
        elif expression['Type'] == 'Var':
            return self.__get_var(expression)['LatteType']['TypeName']
        elif expression['Type'] == 'FunCall':
            return self.__eval_expression_type_funcall(expression)
        else:
            raise InvalidExpression('ERROR: unrecognized expression type')

    def __typecheck_statement(self, statement):
        if statement['Type'] == 'VariableDecl':
            self.__typecheck_var_decl(statement)
        elif statement['Type'] in ['IfStmt', 'IfElseStmt']:
            self.__typecheck_if_stmt(statement)
        elif statement['Type'] == 'WhileLoop':
            self.__typecheck_while(statement)
        elif statement['Type'] == 'End':
            pass
        elif statement['Type'] == 'Expr':
            try:
                self.__eval_expression_type(statement['Expr'])
            except (InvalidExpression, VariableUndeclared) as e:
                self.errors.append(e.msg)
        elif statement['Type'] == 'Block':
            self.__typecheck_block(statement)
        elif statement['Type'] == 'Assignment':
            self.__typecheck_assignment(statement)
        elif statement['Type'] == 'IncDec':
            self.__typecheck_inc_dec(statement)
        elif statement['Type'] == 'Return':
            self.__typecheck_return(statement)
        else:
            raise InvalidStatementType('ERROR: unrecognized type of statement,\
line: %d, pos: %d - %d', (statement['LineNo'],\
                statement['StartPos'], statement['EndPos']))


    def __typecheck_return(self, statement):
        if statement['Type'] != 'Return':
            raise InvalidStatementType('ERROR: not a return statement')
        try:
            expr_type = None
            if statement['Expr']:
                expr_type = self.__eval_expression_type(statement['Expr'])
            if self.__current_function['LatteType'] == 'void' and expr_type:
                self.errors.append('ERROR: in return statement: returning value of type %s\
in function %s declared not to return anything, line %d, pos: %d - %d'%\
                        (expr_type, self.__current_function['Name'], statement['LineNo'],\
                        statement['StartPos'], statement['EndPos']))
                return;
            if self.__current_function['LatteType']['TypeName'] != 'void' and not expr_type:
                self.errors.append('ERROR: in return statement: returning without value, \
while function %s declared to return value of type %s, line %d, pos: %d - %d' %\
                        (self.__current_function['Name'], self.__current_function['LatteType']['TypeName'],
                            statement['LineNo'], statement['StartPos'], statement['EndPos']))
                return;
            if expr_type and expr_type != self.__current_function['LatteType']['TypeName']:
                self.errors.append('ERROR: in return statement: returning value of type %s \
in a function declared to return type %s, line: %d, pos: %d - %d' %\
                        (expr_type, self.__current_function['LatteType']['TypeName'],\
                        statement['LineNo'], statement['StartPos'], statement['EndPos']))

        except (InvalidExpression, VariableUndeclared) as e:
            self.errors.append(e.msg)


    def __typecheck_inc_dec(self, statement):
        if statement['Type'] != 'IncDec':
            raise InvalidStatementType('ERROR: not an increment/decrement statement')
        try:
            if self.__get_var(statement)['LatteType']['TypeName'] != 'int':
                    self.errors.append('ERROR: in increment/decrement statement:\n\
invalid type of variable %s, line: %d pos %d - %d' %\
                            (statement['Name'], statement['LineNo'], \
                            statement['StartPos'], statement['EndPos']))
        except VariableUndeclared as e:
            self.errors.append(e.msg);


    def __typecheck_assignment(self, statement):
        if statement['Type'] != 'Assignment':
            raise InvalidStatementType('ERROR: not an assignment')
        try:
            var_type = self.__get_var(statement)['LatteType']['TypeName']
            expr_type = self.__eval_expression_type(statement['Expr'])
            if  var_type != expr_type:
                self.errors.append('ERROR: in assignment to %s: invalid type of expression being assigned:\n\
expected: %s, got: %s, line: %d pos: %d - %d' % (statement['Name'], var_type, expr_type, statement['LineNo'],\
                    statement['StartPos'], statement['EndPos']))
            #else:
            #    self.__get_var(statement)['Assigned'] = statement['Expr']

        except (VariableUndeclared, InvalidExpression) as e:
            self.errors.append(e.msg)


    def __typecheck_block(self, statement):
        if statement['Type'] != 'Block':
            raise InvalidStatementType('ERROR: not a block statement')
        self.__push_env()
        for internal_statement in statement['Stmts']:
            self.__typecheck_statement(internal_statement)
        self.__pop_env()


    def __typecheck_while(self, statement):
        if statement['Type'] != 'WhileLoop':
            raise InvalidStatementType('ERROR: not a while loop')
        try:
            if self.__eval_expression_type(statement['Condition']) != 'boolean':
                self.errors.append('ERROR: in condition of while loop: invalid type of expression,\n\
line: %d, pos: %d - %d' % (statement['LineNo'],\
                        statement['StartPos'], statement['EndPos']))

        except (InvalidExpression, VariableUndeclared) as e:
            self.errors.append(e.msg)
        self.__push_env()
        self.__typecheck_statement(statement['Stmt'])
        self.__pop_env()


    def __typecheck_var_decl(self, statement):
        if statement['Type'] != 'VariableDecl':
            raise InvalidStatementType('ERROR: not a variable declaration')

        if statement['LatteType']['TypeName'] == 'void':
            self.errors.append('ERROR: in declaration of %s: cannot declare variable of type \'void\', \
line: %d, pos: %d - %d', (statement['Name'], statement['LineNo'],\
                    statement['StartPos'], statement['EndPos']))

        for item in statement['Items']:
            if item['Name'] in self.environments[-1].keys():
                self.errors.append('ERROR: variable %s already declared in this scope, line: %d, pos: %d - %d' %\
                        (item['Name'], item['LineNo'], statement['StartPos'], item['EndPos']))
                continue
            if item['Assigned']:
                try:
                    expr_type = self.__eval_expression_type(item['Assigned'])
                    var_type = statement['LatteType']['TypeName']
                    if  expr_type != var_type:
                        self.errors.append('ERROR: in declaration of %s: invalid type of initializer, \
expected: %s, got: %s, line: %d, position: %d - %d' % (item['Name'], var_type, expr_type, item['LineNo'],\
                            item['StartPos'], item['EndPos']))
                        continue

                except (InvalidExpression, VariableUndeclared) as e:
                    self.errors.append(e.msg)
                    continue

            self.environments[-1][item['Name']] = item
            item['LatteType'] = statement['LatteType']


    def __typecheck_if_stmt(self, statement):
        if statement['Type'] not in ['IfStmt', 'IfElseStmt']:
            raise InvalidStatementType('ERROR: not an if statement!')
        try:
            if self.__eval_expression_type(statement['Condition']) != 'boolean':
                self.errors.append('ERROR: in condition of if statement: invalid type of expression,\
line: %d, pos: %d - %d' % (statement['LineNo'],\
                        statement['StartPos'], statement['EndPos']))
        except (InvalidExpression, VariableUndeclared) as e:
            self.errors.append(e.msg)
        self.__push_env()
        if statement['Type'] == "IfStmt":
           self.__typecheck_statement(statement['Stmt'])
        else:
           self.__typecheck_statement(statement['Stmt1'])
           self.__typecheck_statement(statement['Stmt2'])
        self.__pop_env()


    def __typecheck_program(self):
        for function in self.syntax_tree:
            if not function:
                continue
            self.__current_function = function
            self.__push_env(function)
            for statement in function['Body']['Stmts']:
                self.__typecheck_statement(statement)
            self.__pop_env()


    def __init__(self, syntax_tree):
        self.syntax_tree = syntax_tree
        self.functions = {}
        self.environments = []
        self.errors = []


    def analyze(self):
        self.__load_functions()
        self.__typecheck_program()
        if self.errors:
            for error in  self.errors:
                print >> sys.stderr, error
            print >> sys.stderr, 'ERROR: Semantic analysis failed!'
        else:
            print 'Semantic analysis successful!'
