import sys
from shared.utils    import get_var, VariableUndeclared, MAIN_MANGLING, Logger
from shared.builtins import BUILTINS_INFO

class InvalidExpression(Exception):
    def __init__(self, msg):
        self.msg = msg


class InvalidStatementType(Exception):
    def __init__(self, msg):
        self.msg = msg


class LatteSemanticAnalyzer:

    def __load_functions(self):
        main = None
        for function in self.__syntax_tree:
            if not function:
                continue
            if function['Name'] in self.__functions:
                self.__errors.append('function %s already defined at line %d, \
                        redefined at line: %d' % (function['Name'], \
                        self.__functions['Name']['LineNo'], function['LineNo']))
                continue
            self.__functions[function['Name']] = function
            if function['Name'] == 'main':
                main = function
        if not main:
            self.__errors.append("didn't encounter main function")
            return
        if main['LatteType']['TypeName'] != 'int':
            self.__errors.append('in declaration of function main:\n\
                    main must return value of type int, line: %d' %
                    main['LineNo'])
            return
        # load built-ins:
        self.__functions.update(BUILTINS_INFO)

    def __push_env(self, function = None):
        self.__environments.append({})
        if function:
            for param in function['ListArg']:
                if param['Name'] in self.__environments[-1]:
                    self.__errors.append('repeated argument name %s, in declaration of %s, line: %d, pos: %d - %d' %\
                        (param['Name'], function['Name'], function['LineNo'], function['StartPos'], function['EndPos']))
                    continue
                self.__environments[-1][param['Name']] = param


    def __pop_env(self):
        self.__environments.pop()


    def __eval_expression_type_unary(self, node, key):
        expression = node[key]
        arg_type = self.__eval_expression_type(expression, 'Arg')
        if expression['Op']['Op'] == '!' and\
                arg_type == 'boolean':
            node[key]['EvalType'] = 'boolean'
            return 'boolean'
        elif expression['Op']['Op'] == '-' and\
                arg_type == 'int':
            node[key]['EvalType'] = 'int'
            return 'int'
        elif expression['Op']['Op'] == '!':
            raise InvalidExpression('applying operator \'!\' to non-boolean value of type %s, line: %d, pos: %d - %d' % \
                    (arg_type, expression['LineNo'], expression['StartPos'], expression['EndPos']))
        elif expression['Op']['Op'] == '-':
            raise InvalidExpression('applying operator \'-\' to non-integer value of type %s, line: %d, pos: %d - %d' %\
                    (arg_type, expression['LineNo'], expression['StartPos'], expression['EndPos']))


    def __eval_expression_type_binary(self, node, key):
        expression = node[key]
        left_type = self.__eval_expression_type(expression, 'Left')
        right_type = self.__eval_expression_type(expression, 'Right')
        if expression['Op']['MetaType'] == 'LogOp':
            if left_type != 'boolean' or right_type != 'boolean':
                raise InvalidExpression('operator \'%s\' applied to non-boolean'
                    'expressions, line: %d, pos: %d - %d' % (expression['Op']['Op'],\
                    expression['LineNo'], expression['Left']['StartPos'], expression['Right']['EndPos']))
            node[key]['EvalType'] = 'boolean'
            return 'boolean'
        elif expression['Op']['MetaType'] == 'RelOp' and expression['Op']['Op'] not in ('==', '!='):
            if left_type not in ['int', 'boolean'] or right_type not in ['int', 'boolean'] or\
                    left_type != right_type:
                        raise InvalidExpression('relational operator %s applied to invalid argument types:\n'
                            'expected expression of type \'int\' or \'boolean\''
                            ' - got %s and %s, line: %d, pos: %d - %d' %\
                                (expression['Op']['Op'], left_type, right_type, expression['LineNo'],\
                                expression['Left']['StartPos'], expression['Right']['EndPos']))
            node[key]['EvalType'] = 'boolean'
            return 'boolean'
        elif expression['Op']['Op'] in ('==', '!='):
            if left_type != right_type or left_type == 'void':
                raise InvalidExpression('relational operator %s applied to incalid argument types:\n'
                    'expected expression of type \'%s\', got \'%s\' and \'%s\', line: %d, pos %d - %d' %\
                        (expression['Op']['Op'], left_type, left_type, right_type, expression['LineNo'],
                            expression['Left']['StartPos'], expression['Right']['EndPos']))
            node[key]['EvalType'] = 'boolean'
            return 'boolean'
        elif expression['Op']['MetaType'] == 'ArithmOp' and expression['Op']['Op'] != '+':
            if left_type != 'int' or right_type != 'int':
                raise InvalidExpression('arithmetic operator %s applied to invalid argument types:\n'
                    'expected expression of type \'int\', got \'%s\' and \'%s\', line: %d, pos: %d - %d' %\
                        (expression['Op']['Op'], left_type, right_type, expression['LineNo'],
                            expression['Left']['StartPos'], expression['Right']['EndPos']))
            node[key]['EvalType'] = 'boolean'
            return 'int'
        elif expression['Op']['Op'] == '+':
            if left_type not in ['int', 'string'] or right_type not in ['int', 'string'] or left_type != right_type:
                raise InvalidExpression('arithmetic operator %s applied to invalid argument types:\n'
                    'expected expression of type \'int\' or \'string\', got %s and %s, line: %d, pos: %d - %d' %\
                        (expression['Op']['Op'], left_type, right_type, expression['LineNo'],
                            expression['Left']['StartPos'], expression['Right']['EndPos']))
            node[key]['EvalType'] = left_type
            return left_type


    def __eval_expression_type_funcall(self, node, key):
        expression = node[key]
        if expression['Name'] not in self.__functions:
            raise InvalidExpression('function %s undeclared, line: %d, pos: %d - %d' %\
                    (expression['Name'], expression['LineNo'], expression['StartPos'], expression['EndPos']))
        function = self.__functions[expression['Name']]
        if len(function['ListArg']) != len(expression['ListArg']):
            raise InvalidExpression('invalid number of arguments provided to function %s: '
                'expected: %d, got: %d, line: %d, pos: %d - %d' %\
                            (function['Name'], len(function['ListArg']), len(expression['ListArg']),\
                                expression['LineNo'], expression['StartPos'], expression['EndPos']))
        for index, (arg_expected, arg_provided) in enumerate(zip(function['ListArg'], expression['ListArg'])):
            expr_type = self.__eval_expression_type(expression['ListArg'], index)
            if expr_type != arg_expected['LatteType']['TypeName']:
                raise InvalidExpression('in a call to function %s: expected: %s, got: %s, '
                    'line: %d, pos %d - %d' % (function['Name'], arg_expected['LatteType']['TypeName'],
                            expr_type, expression['LineNo'], expression['StartPos'], expression['EndPos']))
            expression['ListArg'][index]['EvalType'] = arg_expected['LatteType']['TypeName']
            if self.__optimize > 0 and not self.__errors:
                self.__optimizer.simplify_expression(expression['ListArg'], index)
        node[key]['EvalType'] = function['LatteType']['TypeName']
        return function['LatteType']['TypeName']


    def __eval_expression_type(self, node, key):
        expression = node[key]
        if expression['Type'] == 'NumLiteral':
            node[key]['EvalType'] = 'int'
            return 'int'
        elif expression['Type'] == 'BoolLiteral':
            node[key]['EvalType'] = 'boolean'
            return 'boolean'
        elif expression['Type'] == 'StrLiteral':
            node[key]['EvalType'] = 'string'
            return 'string'
        elif expression['Type'] == 'UnaryOp':
            return self.__eval_expression_type_unary(node, key)
        elif expression['Type'] == 'BinaryOp':
            return self.__eval_expression_type_binary(node, key)
        elif expression['Type'] == 'Var':
            var_type = get_var(self.__environments, expression)['LatteType']['TypeName']
            node[key]['EvalType'] = var_type
            return var_type
        elif expression['Type'] == 'FunCall':
            return self.__eval_expression_type_funcall(node, key)
        else:
            raise InvalidExpression('unrecognized expression type')


    def __typecheck_statement(self, statement):
        if statement['Type'] == 'VariableDecl':
            return self.__typecheck_var_decl(statement)
        elif statement['Type'] in ['IfStmt', 'IfElseStmt']:
            return self.__typecheck_if_stmt(statement)
        elif statement['Type'] == 'WhileLoop':
            return self.__typecheck_while(statement)
        elif statement['Type'] == 'End':
            return statement
        elif statement['Type'] == 'Expr':
            try:
                self.__eval_expression_type(statement, 'Expr')
            except (InvalidExpression, VariableUndeclared) as e:
                self.__errors.append(e.msg)
            if self.__optimize > 0 and not self.__errors:
                self.__optimizer.simplify_expression(statement, 'Expr')
            return statement
        elif statement['Type'] == 'Block':
            return self.__typecheck_block(statement)
        elif statement['Type'] == 'Assignment':
            return self.__typecheck_assignment(statement)
        elif statement['Type'] == 'IncDec':
            return self.__typecheck_inc_dec(statement)
        elif statement['Type'] == 'Return':
            return self.__typecheck_return(statement)
        else:
            raise InvalidStatementType('unrecognized type of statement,'
                'line: %d, pos: %d - %d', (statement['LineNo'],\
                statement['StartPos'], statement['EndPos']))


    def __typecheck_return(self, statement):
        if statement['Type'] != 'Return':
            raise InvalidStatementType('not a return statement')
        try:
            expr_type = None
            if statement['Expr']:
                expr_type = self.__eval_expression_type(statement, 'Expr')
                if self.__optimize > 0 and not self.__errors:
                    self.__optimizer.simplify_expression(statement, 'Expr')
            if self.__current_function['LatteType']['TypeName'] == 'void' and expr_type:
                self.__errors.append('in return statement: returning value of type %s'
                    'in function %s declared not to return anything, line %d, pos: %d - %d'%\
                        (expr_type, self.__current_function['Name'], statement['LineNo'],\
                        statement['StartPos'], statement['EndPos']))
                return statement;
            if self.__current_function['LatteType']['TypeName'] != 'void' and not expr_type:
                self.__errors.append('in return statement: returning without value, '
                    'while function %s declared to return value of type %s, line %d, pos: %d - %d' %\
                        (self.__current_function['Name'], self.__current_function['LatteType']['TypeName'],
                            statement['LineNo'], statement['StartPos'], statement['EndPos']))
                return statement;
            if expr_type and expr_type != self.__current_function['LatteType']['TypeName']:
                self.__errors.append('in return statement: returning value of type %s '
                    'in a function declared to return type %s, line: %d, pos: %d - %d' %\
                        (expr_type, self.__current_function['LatteType']['TypeName'],\
                        statement['LineNo'], statement['StartPos'], statement['EndPos']))

        except (InvalidExpression, VariableUndeclared) as e:
            self.__errors.append(e.msg)
        return statement


    def __typecheck_inc_dec(self, statement):
        if statement['Type'] != 'IncDec':
            raise InvalidStatementType('not an increment/decrement statement')
        try:
            if get_var(self.__environments, statement)['LatteType']['TypeName'] != 'int':
                    self.__errors.append('in increment/decrement statement:\n'
                        'invalid type of variable %s, line: %d pos %d - %d' %\
                            (statement['Name'], statement['LineNo'], \
                            statement['StartPos'], statement['EndPos']))
        except VariableUndeclared as e:
            self.__errors.append(e.msg);
        return statement


    def __typecheck_assignment(self, statement):
        if statement['Type'] != 'Assignment':
            raise InvalidStatementType('not an assignment')
        try:
            var_type = get_var(self.__environments, statement)['LatteType']['TypeName']
            expr_type = self.__eval_expression_type(statement, 'Expr')
            if  var_type != expr_type:
                self.__errors.append('in assignment to %s: invalid type of expression being assigned:\n'
                    'expected: %s, got: %s, line: %d pos: %d - %d' % (statement['Name'],
                        var_type, expr_type, statement['LineNo'],  statement['StartPos'], statement['EndPos']))
                return statement
            #else:
            #    get_var(self.__environments, statement)['Assigned'] = statement['Expr']
            if self.__optimize > 0 and not self.__errors:
                self.__optimizer.simplify_expression(statement, 'Expr')
        except (VariableUndeclared, InvalidExpression) as e:
            self.__errors.append(e.msg)
        return statement


    def __typecheck_block(self, statement):
        if statement['Type'] != 'Block':
            raise InvalidStatementType('not a block statement')
        self.__push_env()
        new_stmt_list = []
        for internal_statement in statement['Stmts']:
            new_stmt_list.append(self.__typecheck_statement(internal_statement))
            if internal_statement['Returns']:
                statement['Returns'] = True
        statement['Stmts'] = new_stmt_list
        self.__pop_env()
        return statement


    def __typecheck_while(self, statement):
        if statement['Type'] != 'WhileLoop':
            raise InvalidStatementType('not a while loop')
        try:
            if self.__eval_expression_type(statement, 'Condition') != 'boolean':
                self.__errors.append('in condition of while loop: invalid type of expression,\n'
                    'line: %d, pos: %d - %d' % (statement['LineNo'],\
                        statement['StartPos'], statement['EndPos']))

        except (InvalidExpression, VariableUndeclared) as e:
            self.__errors.append(e.msg)
        if self.__optimize > 0 and not self.__errors:
            self.__optimizer.simplify_expression(statement, 'Condition')
        self.__push_env()
        statement['Stmt'] = self.__typecheck_statement(statement['Stmt'])
        self.__pop_env()
        if statement['Condition']['EvalType'] in ('BoolLiteral', 'NumLiteral') and\
            not statement['Condition']['Value']:
            return {'Type': 'End', 'Returns': False,
                        'StartPos': statement['StartPos'], 'EndPos': statement['EndPos']}
        if statement['Stmt']['Returns']:
            statement['Returns'] = True
        return statement


    def __typecheck_var_decl(self, statement):
        if statement['Type'] != 'VariableDecl':
            raise InvalidStatementType('not a variable declaration')

        if statement['LatteType']['TypeName'] == 'void':
            self.__errors.append('in declaration of %s: cannot declare variable of type \'void\', '
                'line: %d, pos: %d - %d', (statement['Name'], statement['LineNo'],\
                    statement['StartPos'], statement['EndPos']))

        for item in statement['Items']:
            if item['Name'] in self.__environments[-1]:
                self.__errors.append('variable %s already declared in this scope, line: %d, pos: %d - %d' %\
                        (item['Name'], item['LineNo'], statement['StartPos'], item['EndPos']))
                continue
            if item['Assigned']:
                try:
                    expr_type = self.__eval_expression_type(item, 'Assigned')
                    var_type = statement['LatteType']['TypeName']
                    if  expr_type != var_type:
                        self.__errors.append('in declaration of %s: invalid type of initializer, '
                            'expected: %s, got: %s, line: %d, position: %d - %d' %\
                                (item['Name'], var_type, expr_type, item['LineNo'],\
                                item['StartPos'], item['EndPos']))
                        continue

                except (InvalidExpression, VariableUndeclared) as e:
                    self.__errors.append(e.msg)
                    continue
                if self.__optimize > 0 and not self.__errors:
                    self.__optimizer.simplify_expression(item, 'Assigned')
            self.__environments[-1][item['Name']] = item
            item['LatteType'] = statement['LatteType']
        return statement


    def __typecheck_if_stmt(self, statement):
        if statement['Type'] not in ['IfStmt', 'IfElseStmt']:
            raise InvalidStatementType('not an if statement!')
        try:
            if self.__eval_expression_type(statement, 'Condition') != 'boolean':
                print statement['Condition']
                print statement['EvalType']
                self.__errors.append('in condition of if statement: invalid type of expression,'
                    'line: %d, pos: %d - %d' % (statement['LineNo'],\
                        statement['StartPos'], statement['EndPos']))
        except (InvalidExpression, VariableUndeclared) as e:
            self.__errors.append(e.msg)
        if self.__optimize > 0 and not self.__errors:
            self.__optimizer.simplify_expression(statement, 'Condition')
        self.__push_env()
        if statement['Type'] == 'IfStmt':
            statement['Stmt'] = self.__typecheck_statement(statement['Stmt'])
        else:
            statement['Stmt1'] = self.__typecheck_statement(statement['Stmt1'])
            statement['Stmt2'] = self.__typecheck_statement(statement['Stmt2'])
        self.__pop_env()
        if statement['Type'] == 'IfStmt' and statement['Stmt']['Returns']:
            statement['Returns'] = True
        elif statement['Type'] == 'IfElseStmt' and statement['Stmt1']['Returns'] and\
                statement['Stmt2']['Returns']:
            statement['Returns'] = True
        if statement['Condition']['Type'] in ('BoolLiteral', 'NumLiteral') and\
                statement['Condition']['Value']:
            return statement['Stmt' if statement['Type'] == 'IfStmt' else 'Stmt1']
        elif statement['Condition']['Type'] in ('BoolLiteral', 'NumLiteral'):
            if statement['Type'] == 'IfElseStmt':
                return statement['Stmt2']
            else:
                return {'Type': 'End', 'Returns': False,
                        'StartPos': statement['StartPos'], 'EndPos': statement['EndPos']}
        return statement


    def __typecheck_program(self):
        new_syntax_tree = []
        for function in self.__syntax_tree:
            if not function:
                continue
            self.__current_function = function
            self.__push_env(function)

            function['Body']['Stmts'] =\
                [self.__typecheck_statement(stmt) for stmt in function['Body']['Stmts']]

            if function['LatteType']['TypeName'] != 'void':
                returns = False
                for stmt in function['Body']['Stmts']:
                    if stmt['Returns']:
                        returns = True
                if not returns:
                    self.__errors.append('function %s declared to return value of type %s '
                        'returns no value, line: %d, pos: %d - %d' % (function['Name'],
                            function['LatteType']['TypeName'], function['LineNo'],
                            function['StartPos'], function['EndPos']))
            self.__pop_env()
            if function['Name'] == 'main':
                function['Name'] = 'main_%d' % MAIN_MANGLING
            new_syntax_tree.append(function)
        self.__syntax_tree = new_syntax_tree

    def get_functions(self):
        return self.__functions

    def __init__(self, syntax_tree, optimizer):
        self.__syntax_tree = syntax_tree
        self.__functions = {}
        self.__environments = []
        self.__errors = []
        self.__optimizer = optimizer
        self.__logger = Logger()


    def analyze(self, optimize):
        self.__optimize = optimize
        self.__load_functions()
        self.__typecheck_program()
        if self.__errors:
            for error in  self.__errors:
                self.__logger.error(error)
            return False
        else:
            return True
