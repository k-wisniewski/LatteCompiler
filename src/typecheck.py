import sys
from shared.utils    import get_var, get_function, VariableUndeclared, MAIN_MANGLING, Logger, is_a
from shared.builtins import BUILTINS_INFO

class InvalidExpression(Exception):
    def __init__(self, msg):
        self.msg = msg


class InvalidStatementType(Exception):
    def __init__(self, msg):
        self.msg = msg


class ClassEnv:
    def __init__(self):
        self.attributes = {}
        self.extends = None
        self.methods = {}

class LatteSemanticAnalyzer:

    def __load_functions(self):
        main = None
        for function in (top_def for top_def in self.__syntax_tree if top_def['Type'] == 'FunDecl'):
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


    def __load_classes(self):
        for class_ in (top_def for top_def in self.__syntax_tree if top_def['Type'] == 'ClassDecl'):
            self.__class_envs[class_['Name']] = ClassEnv()
            self.__class_envs[class_['Name']].methods = \
                    [member for member in class_['Members'] if member['Type'] == 'MethodDecl']
            self.__class_envs[class_['Name']].attributes = \
                    [member for member in class_['Members'] if member['Type'] == 'FieldDecl']


    def __get_var_type(self, statement):
        if statement['LValue']['Type'] == 'LVar':
            variable = get_var(self.__function_envs, statement['LValue'],
                    self.__class_envs, self.__current_class)
        elif statement['LValue']['Type'] == 'LArrSubscript':
            variable = get_var(self.__function_envs, statement['LValue'],
                    self.__class_envs, self.__current_class)
            subscript_type, meta_type = self.__eval_expression_type(statement['LValue']['Subscript'])
            if subscript_type != 'int' and meta_type != 'Primitive':
                self.__errors.append('array indices must be integers, not %s%s, line: %d, pos: %d - %d' %
                    (subscript_type, self.__arr(meta_type), statement['LineNo'],
                        statement['StartPos']. statement['EndPos']))
        elif statement['LValue']['Type'] == 'LAttribute':
            variable = get_var(self.__function_envs, statement['LValue'],
                    self.__class_envs, self.__current_function)
            attr = statement['LValue']['Attr']
            class_env = self.__class_envs[variable['LatteType']['Typename']]
            if variable['LatteType']['MetaType'] != 'Class':
                self.__errors.append('arrays and primitive types don\'t have l-value attributes, line %d, pos: %d - %d' %
                    (statement['LineNo'], statement['StartPos'], statement['EndPos']))
            if attr  not in class_env:
                self.__errors.append('objects of class %s do not have attribute %s, line: %d, pos: %d - %d' %
                    (variable['TypeName']['LatteType'], statement['LineNo'], statement['StartPos'], statement['EndPos']))
            else:
                variable = class_env.attributes[attr]
        return variable['LatteType']['TypeName'], variable['LatteType']['MetaType']


    def __push_env(self, function = None):
        self.__function_envs.append({})
        if function:
            for param in function['ListArg']:
                if param['Name'] in self.__function_envs[-1]:
                    self.__errors.append('repeated argument name %s, in declaration of %s, line: %d, pos: %d - %d' %\
                        (param['Name'], function['Name'], function['LineNo'], function['StartPos'], function['EndPos']))
                    continue
                self.__function_envs[-1][param['Name']] = param


    def __pop_env(self):
        self.__function_envs.pop()


    def __find_cycle(self, class_):
        current = class_['Extends']
        previous = class_['Extends']
        traveled = 0
        while True:
            current = self.__class_envs[current].extends
            if (traveled % 2):
                previous = self.__class_envs[previous].extends
            if current == traveled:
               return True
            elif not current:
                break
        return False


    def __eval_expression_type_unary(self, node, key):
        expression = node[key]
        arg_type, meta_type = self.__eval_expression_type(expression, 'Arg')
        if meta_type != 'Primitive':
            raise InvalidExpression('unary operators work only with primitive types')
        if expression['Op']['Op'] == '!' and\
                arg_type == 'boolean':
            node[key]['EvalType'] = 'boolean'
            node[key]['EvalMetaType'] = 'Primitive'
            return 'boolean', 'Primitive'
        elif expression['Op']['Op'] == '-' and\
                arg_type == 'int':
            node[key]['EvalType'] = 'int'
            node[key]['EvalMetaType'] = 'Primitive'
            return 'int', 'Primitive'
        elif expression['Op']['Op'] == '!':
            raise InvalidExpression('applying operator \'!\' to non-boolean value of type %s, line: %d, pos: %d - %d' % \
                    (arg_type, expression['LineNo'], expression['StartPos'], expression['EndPos']))
        elif expression['Op']['Op'] == '-':
            raise InvalidExpression('applying operator \'-\' to non-integer value of type %s, line: %d, pos: %d - %d' %\
                    (arg_type, expression['LineNo'], expression['StartPos'], expression['EndPos']))


    def __eval_expression_type_binary(self, node, key):
        expression = node[key]
        left_type, left_meta_type = self.__eval_expression_type(expression, 'Left')
        right_type, right_meta_type = self.__eval_expression_type(expression, 'Right')

        if left_meta_type != 'Primitive' or right_meta_type != 'Primitive':
            raise InvalidExpression('binary operations can only work with primitives, line: %d, pos: %d - %d' %
                    (expression['LineNo'], expression['StartPos'], expression['EndPos']))

        if expression['Op']['MetaType'] == 'LogOp':
            if left_type != 'boolean' or right_type != 'boolean':
                raise InvalidExpression('operator \'%s\' applied to non-boolean'
                    'expressions, line: %d, pos: %d - %d' % (expression['Op']['Op'],\
                    expression['LineNo'], expression['Left']['StartPos'], expression['Right']['EndPos']))
            node[key]['EvalType'] = 'boolean'
            node[key]['EvalMetaType'] = 'Primitive'
            return 'boolean', 'Primitive'
        elif expression['Op']['MetaType'] == 'RelOp' and expression['Op']['Op'] not in ('==', '!='):
            if left_type not in ['int', 'boolean'] or right_type not in ['int', 'boolean'] or\
                    left_type != right_type:
                        raise InvalidExpression('relational operator %s applied to invalid argument types:\n'
                            'expected expression of type \'int\' or \'boolean\''
                            ' - got %s and %s, line: %d, pos: %d - %d' %\
                                (expression['Op']['Op'], left_type, right_type, expression['LineNo'],\
                                expression['Left']['StartPos'], expression['Right']['EndPos']))
            node[key]['EvalType'] = 'boolean'
            node[key]['EvalMetaType'] = 'Primitive'
            return 'boolean', 'Primitive'
        elif expression['Op']['Op'] in ('==', '!='):
            if left_type != right_type or left_type == 'void':
                raise InvalidExpression('relational operator %s applied to incalid argument types:\n'
                    'expected expression of type \'%s\', got \'%s\' and \'%s\', line: %d, pos %d - %d' %\
                        (expression['Op']['Op'], left_type, left_type, right_type, expression['LineNo'],
                            expression['Left']['StartPos'], expression['Right']['EndPos']))
            node[key]['EvalType'] = 'boolean'
            return 'boolean', 'Primitive'
        elif expression['Op']['MetaType'] == 'ArithmOp' and expression['Op']['Op'] != '+':
            if left_type != 'int' or right_type != 'int':
                raise InvalidExpression('arithmetic operator %s applied to invalid argument types:\n'
                    'expected expression of type \'int\', got \'%s\' and \'%s\', line: %d, pos: %d - %d' %\
                        (expression['Op']['Op'], left_type, right_type, expression['LineNo'],
                            expression['Left']['StartPos'], expression['Right']['EndPos']))
            node[key]['EvalType'] = 'int'
            node[key]['EvalMetaType'] = 'Primitive'
            return 'int', 'Primitive'
        elif expression['Op']['Op'] == '+':
            if left_type not in ['int', 'string'] or right_type not in ['int', 'string'] or left_type != right_type:
                raise InvalidExpression('arithmetic operator %s applied to invalid argument types:\n'
                    'expected expression of type \'int\' or \'string\', got %s and %s, line: %d, pos: %d - %d' %\
                        (expression['Op']['Op'], left_type, right_type, expression['LineNo'],
                            expression['Left']['StartPos'], expression['Right']['EndPos']))
            node[key]['EvalType'] = left_type
            node[key]['EvalMetaType'] = 'Primitive'
            return left_type, 'Primitive'


    def __eval_expression_type_funcall(self, node, key):
        expression = node[key]
        function = get_function(expression, self.__functions, self.__class_envs, self.__current_class)
        if len(function['ListArg']) != len(expression['ListArg']):
            raise InvalidExpression('invalid number of arguments provided to function %s: '
                'expected: %d, got: %d, line: %d, pos: %d - %d' %\
                            (function['Name'], len(function['ListArg']), len(expression['ListArg']),\
                                expression['LineNo'], expression['StartPos'], expression['EndPos']))
        for index, (arg_expected, arg_provided) in enumerate(zip(function['ListArg'], expression['ListArg'])):
            expr_type, meta_type = self.__eval_expression_type(expression['ListArg'], index)
            if not is_a(expr_type, meta_type, arg_expected['LatteType']['TypeName'],
                    arg_expected['LatteType']['MetaType'], self.__class_envs):
                raise InvalidExpression('in a call to function %s: expected: %s, got: %s, '
                    'line: %d, pos %d - %d' % (function['Name'], arg_expected['LatteType']['TypeName'],
                            expr_type, expression['LineNo'], expression['StartPos'], expression['EndPos']))
            expression['ListArg'][index]['EvalType'] = arg_expected['LatteType']['TypeName']
            expression['ListArg'][index]['EvalMetaType'] = arg_expected['LatteType']['MetaType']
            if self.__optimize > 0 and not self.__errors:
                self.__optimizer.simplify_expression(expression['ListArg'], index)
        node[key]['EvalType'] = function['LatteType']['TypeName']
        node[key]['EvalType'] = function['LatteType']['MetaType']
        return function['LatteType']['TypeName'], function['LatteType']['MetaType']


    def __eval_expression_var(self, node, key):
        var_type = get_var(self.__function_envs, node[key])['LatteType']
        node[key]['EvalType'] = var_type['TypeName']
        node[key]['EvalMetaType'] = var_type['MetaType']
        return var_type['TypeName'], var_type['MetaType']


    def __eval_expression_type_new_arr(self, node, key):
        pass


    def __eval_expression_type_new_object(self, node, key):
        pass


    def __eval_expression_type_attribute(self, node, key):
        pass


    def __eval_expression_type_method_call(self, node, key):
        pass


    def __eval_expression_type_cast(self, node, key):
        pass


    def __eval_expression_type_null(self, node, key):
        pass


    def __eval_expression_type(self, node, key):
        expression = node[key]
        if expression['Type'] == 'NumLiteral':
            node[key]['EvalType'] = 'int'
            node[key]['EvalMetaType'] = 'Primitive'
            return 'int', 'Primitive'
        elif expression['Type'] == 'BoolLiteral':
            node[key]['EvalType'] = 'boolean'
            node[key]['EvalMetaType'] = 'Primitive'
            return 'boolean', 'Primitive'
        elif expression['Type'] == 'StrLiteral':
            node[key]['EvalType'] = 'string'
            node[key]['EvalMetaType'] = 'Primitive'
            return 'string', 'Primitive'
        elif expression['Type'] == 'UnaryOp':
            return self.__eval_expression_type_unary(node, key)
        elif expression['Type'] == 'BinaryOp':
            return self.__eval_expression_type_binary(node, key)
        elif expression['Type'] == 'Var':
            return self.__eval_expression_var(node, key)
        elif expression['Type'] == 'FunCall':
            return self.__eval_expression_type_funcall(node, key)
        elif expression['Type'] in ('NewArrayPrimitive', 'NewArrayObject'):
            return self.__eval_expression_type_new_arr(node, key)
        elif expression['Type'] == 'NewObject':
            return self.__eval_expression_type_new_object(node, key)
        elif expression['Type'] == 'Attribute':
            return self.__eval_expression_type_attribute(node, key)
        elif expression['Type'] == 'MethodCall':
            return self.__eval_expression_type_method_call(node, key)
        elif expression['Type'] == 'Cast':
            return self.__eval_expression_type_cast(node, key)
        elif expression['Type'] == 'Null':
            return self.__eval_expression_type_null(node, key)
        else:
            raise InvalidExpression('unrecognized expression type')



    def __typecheck_return(self, statement):
        if statement['Type'] != 'Return':
            raise InvalidStatementType('not a return statement')
        try:
            expr_type = None
            expr_type, meta_type = None, None
            if statement['Expr']:
                expr_type, meta_type = self.__eval_expression_type(statement, 'Expr')
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
            if expr_type and not is_a(expr_type, meta_type, self.__current_function['LatteType']['TypeName'],
                    self.__current_function['LatteType']['MetaType'], self.__class_envs):
                self.__errors.append('in return statement: returning value of type %s '
                    'in a function declared to return type %s, line: %d, pos: %d - %d' %\
                        (expr_type, self.__current_function['LatteType']['TypeName'],\
                        statement['LineNo'], statement['StartPos'], statement['EndPos']))
            if meta_type and meta_type != self.__current_function['LatteType']['MetaType']:
                 self.__errors.append('in return statement: returning %s '
                    'in a function declared to return %s, line: %d, pos: %d - %d' %\
                        (meta_type, self.__current_function['LatteType']['MetaType'],\
                        statement['LineNo'], statement['StartPos'], statement['EndPos']))

        except (InvalidExpression, VariableUndeclared) as e:
            self.__errors.append(e.msg)
        return statement


    def __typecheck_inc_dec(self, statement):
        if statement['Type'] != 'IncDec':
            raise InvalidStatementType('not an increment/decrement statement')
        try:
            var_type, var_meta_type = self.__get_var_type(statement)
            if var_type != 'int':
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
            if statement['LValue']['Type'] not in ('LVar', 'LArrSubscript', 'LAttribute'):
                self.__errors.append('assigning to r-value, line: %d, pos: %d - %d' %
                    (statement['LineNo'], statement['StartPos'], statement['EndPos']))
                return statement
            var_type, var_meta_type = self.__get_var_type(statement)
            expr_type, meta_type = self.__eval_expression_type(statement, 'Expr')
            if var_meta_type == 'Array' and\
                    statement['Expr']['Type'] not in ('NewArrayObject', 'NewArrayPrimitive'):
                self.__errors.append('array can only be assigned with newly created object, line: %d, pos %d - %d' %
                    (statement['LineNo'], statement['StartPos'], statement['EndPos']))
            if not is_a(expr_type, meta_type, var_type, var_meta_type, self.__class_envs):
                self.__errors.append('in assignment to %s: invalid type of expression being assigned:\n'
                    'expected: %s, got: %s, line: %d pos: %d - %d' % (statement['LatteType']['TypeName'],
                        var_type, expr_type, statement['LineNo'],  statement['StartPos'], statement['EndPos']))
                return statement
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
            condition_expr_type, condition_meta_type = self.__eval_expression_type(statement, 'Condition')
            if condition_expr_type != 'boolean' and condition_meta_type != 'Primitive':
                self.__errors.append('in condition of while loop: invalid type of expression,\n'
                    'line: %d, pos: %d - %d' % (statement['LineNo'],\
                        statement['StartPos'], statement['EndPos']))

        except (InvalidExpression, VariableUndeclared) as e:
            self.__errors.append(e.msg)
            return statement
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

    def __typecheck_for(self, statement):
        if statement['Type'] != 'ForLoop':
            raise InvalidStatementType('not a for loop')
        looped_over = get_var(self.__function_envs, statement, self.__class_envs, self.__current_class)
        if looped_over['LatteType']['MetaType'] != 'Array':
            self.__errors.append('cannot iterate over %s: not an array type, line: %s, pos: %d - %d' %
                (looped_over['LatteType']['TypeName'], looped_over['LineNo'],
                    looped_over['StartPos'], looped_over['EndPos']))
        if not is_a(statement['LoopVar']['LatteType']['TypeName'], statement['LoopVar']['LatteType']['MetaType'],
                looped_over['LatteType']['TypeName'], looped_over['LatteType']['MetaType']):
            self.__errors.append('invalid type of for-loop variable: got: %s, expected: %s, line: %d, pos: %d - %d' %
                (statement['LoopVar']['LatteType']['TypeName'], looped_over['LatteType']['TypeName'][:-2],
                    statement['LineNo'], statement['StartPos'], statement['EndPos']))
        self.__push_env()

        self.__typecheck_statement(statement['Stmt'])
        self.__function_envs[-1][statement['LoopVar']['Name']] = statement['LoopVar']
        self.__pop_env()
        if statement['Stmt']['Returns']:
            statement['Returns'] = True

        return statement



    def __typecheck_var_decl(self, statement):
        if statement['Type'] not in ('VariableDecl', 'FieldDecl'):
            raise InvalidStatementType('not a variable declaration')

        if statement['LatteType']['TypeName'] == 'void':
            self.__errors.append('in declaration of %s: cannot declare variable of type \'void\', '
                'line: %d, pos: %d - %d', (statement['Name'], statement['LineNo'],\
                    statement['StartPos'], statement['EndPos']))

        for item in statement['Items']:
            if (statement['Type'] == 'VariableDecl' and item['Name'] in self.__function_envs[-1]) or\
                    (statement['Type'] == 'FieldDecl' and\
                    item['Name'] in self.__class_envs[self.__current_class['Name']].attributes):
                self.__errors.append('variable %s already declared in this scope, line: %d, pos: %d - %d' %\
                        (item['Name'], item['LineNo'], statement['StartPos'], item['EndPos']))
                continue
            if item['Assigned']:
                try:
                    expr_type, meta_type = self.__eval_expression_type(item, 'Assigned')
                    var_type = statement['LatteType']['TypeName']
                    var_meta_type = statement['LatteType']['MetaType']
                    if  not is_a(expr_type, meta_type, var_type, var_meta_type, self.__class_envs):
                        arr = lambda meta: '[]' if meta == 'Array' else ''
                        self.__errors.append('in declaration of %s: invalid type of initializer, '
                            'expected: %s%s, got: %s%s, line: %d, position: %d - %d' %
                                (item['Name'], var_type, self.__arr(var_meta_type), expr_type,
                                self.__arr(meta_type), self.__arr(meta_type),
                                item['LineNo'], item['StartPos'], item['EndPos']))
                        continue

                except (InvalidExpression, VariableUndeclared) as e:
                    self.__errors.append(e.msg)
                    continue
                if self.__optimize > 0 and not self.__errors:
                    self.__optimizer.simplify_expression(item, 'Assigned')
            self.__function_envs[-1][item['Name']] = item
            item['LatteType'] = statement['LatteType']
        return statement


    def __typecheck_if_stmt(self, statement):
        if statement['Type'] not in ['IfStmt', 'IfElseStmt']:
            raise InvalidStatementType('not an if statement!')
        try:
            if self.__eval_expression_type(statement, 'Condition') != ('boolean', 'Primitive'):
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
        if statement['Condition']['Type']  == 'BoolLiteral' and\
                statement['Condition']['Value']:
            return statement['Stmt' if statement['Type'] == 'IfStmt' else 'Stmt1']
        elif statement['Condition']['Type'] == 'BoolLiteral':
            if statement['Type'] == 'IfElseStmt':
                return statement['Stmt2']
            else:
                return {'Type': 'End', 'Returns': False,
                        'StartPos': statement['StartPos'], 'EndPos': statement['EndPos']}
        return statement


    def __check_if_function_returns(self, function):
        # TODO
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
        elif statement['Type'] == 'ForLoop':
            return self.__typecheck_for(statement)
        else:
            raise InvalidStatementType('unrecognized type of statement,'
                'line: %d, pos: %d - %d', (statement['LineNo'],\
                statement['StartPos'], statement['EndPos']))


    def __typecheck_function(self, function):
        self.__current_function = function
        self.__push_env(function)
        function['Body']['Stmts'] =\
            [self.__typecheck_statement(stmt) for stmt in function['Body']['Stmts']]
        self.__check_if_function_returns(function)
        self.__pop_env()
        return function


    def __typecheck_member(self, member):
        if member['Type'] == 'FieldDecl':
            return self.__typecheck_var_decl(member)
        elif member['Type'] == 'MethodDecl':
            return self.__typecheck_function(member)


    def __typecheck_class(self, class_):
        self.__current_class = class_
        if class_['Extends'] in self.__class_envs:
            if self.__find_cycle(class_):
                self.__errors.append('There\'s a cycle in class hierarchy! Class %s cannot extend class %s,'
                        ' line: %d, pos: %d - %d' % (class_['Name'], class_['Extends'],
                            class_['LineNo'], class_['StartPos'], class_['EndPos']))
                return class_
            self.__class_envs[class_['Name']].extends = self.__class_envs[class_['Extends']]
        elif class_['Extends']:
            self.__errors.append('class %s extends non-existent class %s, line: %d, pos: %d - %d' %
                    (class_['Name'], class_['Extends'], class_['LineNo'],
                        class_['StartPos'], class_['EndPos']))
        class_['Members'] =\
            [self.__typecheck_member(member) for member in class_['Members']]
        self.__current_class = None
        return class_



    def __typecheck_program(self):
        new_syntax_tree = []
        for top_def in self.__syntax_tree:
            if not top_def:
                continue
            if top_def['Type'] == 'FunDecl':
                top_def = self.__typecheck_function(top_def)
            else:
                top_def = self.__typecheck_class(top_def)
            new_syntax_tree.append(top_def)
        self.__syntax_tree = new_syntax_tree

    def get_functions(self):
        return self.__functions

    def __init__(self, syntax_tree, optimizer, target, logger):
        self.__syntax_tree = syntax_tree
        self.__functions = {}
        self.__function_envs = []
        self.__class_envs = {}
        self.__errors = []
        self.__optimizer = optimizer
        self.__current_class = None
        self.__logger = logger
        self.__target = target


    def analyze(self, optimize):
        self.__optimize = optimize
        self.__load_functions()
        self.__load_classes()
        self.__typecheck_program()
        if self.__errors:
            for error in  self.__errors:
                self.__logger.error(error)
            return False
        else:
            return True
