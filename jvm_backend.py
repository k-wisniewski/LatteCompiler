from utils import get_var
OPTIMIZED_LIMIT = 4


RELATIONAL_MNEMONICS = {
#   OP       NORM    NEG     REV     NEG_REV BIN_NORM    BIN_NEG
    '<'  : ('iflt', 'ifge', 'ifgt', 'ifle', 'if_cmplt', 'if_cmpge'),
    '<=' : ('ifle', 'ifgt', 'ifge', 'iflt', 'if_cmple', 'if_cmpgt'),
    '>'  : ('ifgt', 'ifle', 'iflt', 'ifge', 'if_cmpgt', 'if_cmple'),
    '>=' : ('ifge', 'iflt', 'ifle', 'ifgt', 'if_cmpge', 'if_cmplt'),
    '==' : ('ifeq', 'ifne', 'ifeq', 'ifne', 'if_cmpeq', 'if_cmpne'),
    '!=' : ('ifne', 'ifeq', 'ifne', 'ifeq', 'if_cmpne', 'if_cmpeq')
}

NORM        = 0
NEG         = 1
REV         = 2
NEG_REV     = 3
BIN_NORM    = 4
BIN_NEG     = 5

class JVM_Backend:
    def __init__(self, syntax_tree, functions):
        self.__syntax_tree = syntax_tree
        self.__jasmin_strings = ['.class public default_class\n'
            '.super java/lang/Object\n']
        self.__locals_counter = 0
        self.__stack_limit = 0
        self.__label_counter = 0
        self.__functions = {function['Name']: function for function in functions}
        self.__environments = []


    def emit(self, text):
        self.current_function.append(text)


    def emit_expr_arithm(self, expr):
        self.emit_expr(expr['Left'])
        self.emit_expr(expr['Right'])
        if expr['Op']['Op'] == '+':
            if expr['EvalType'] == 'string':
                self.emit('invokevirtual java/lang/String.concat')
            else:
                self.emit('iadd')
        elif expr['Op']['Op'] == '-':
            self.emit('isub')
        elif expr['Op']['Op'] == '*':
            self.emit('imul')
        elif expr['Op']['Op'] == '/':
            self.emit('idiv')
        elif expr['Op']['Op'] == '%':
            self.emit('irem')


    def emit_expr_log(expr, jump_if_true=None, jump_if_false=None, next_label=None):
        false_label = jump_if_false if jump_if_false else 'LFALSE%d' % self.__label_counter
        true_label = jump_if_true if jump_if_true else 'LTRUE%d' % self.__label_counter
        self.__label_counter += 1
        if expr['Op']['Op'] == '&&':
            next_condition_label = 'LTRUE%d' % self.__label_counter
            self.emit_expr(expr['Left'], next_condition_label, false_label, next_condition_label)
            self.emit(next_condition_label)
            self.emit_expr(expr['Right'], jump_if_false=false_label)
            if jump_if_true:
                self.emit('goto %s\n' % true_label)
            else:
                self.emit('iconst_1\n')
                self.emit('goto LEND%d\n' % self.__label_counter)
            if not jump_if_false:
                self.emit('LFALSE%d:\n' % self.__label_counter)
                self.emit('iconst_0\n')
            if not jump_if_true and not jump_if_false:
                self.emit('LEND%d:\n' % self.__label_counter)

        elif expr['Op']['Op'] == '||':
            next_condition_label = 'LFALSE%d' % self.__label_counter
            self.emit_expr(expr['Left'], true_label, next_condition_label, next_condition_label)
            self.emit(next_condition_label + '\n')
            self.emit_expr(expr['Right'], true_label, )
            if jump_if_false:
                if next_label != jump_if_false or not next_label:
                    self.emit('goto %s' % jump_if_false)
            else:
                self.emit('iconst_0\n')
                self.emit('goto LEND%d\n' % self.__label_counter)
            if not jump_if_true:
                self.emit('LTRUE%d:\n' % self.__label_counter)
                self.emit('iconst_0\n')
            if not jump_if_true and not jump_if_false:
                self.emit('LEND%d:\n' % self.__label_counter)

        self.__label_counter += 1


    def emit_expr_rel(self, expr, jump_if_true=None, jump_if_false=None, next_label=None):
        true_label = jump_if_true if jump_if_true else 'LTRUE%d' % self.__label_counter
        if expr['Left']['Type'] in ('BoolLiteral', 'NumLiteral') and not expr['Left']['Value']:
            self.emit_expr(expr['Right'])
            self.emit(RELATIONAL_MNEMONICS[expr['Op']['Op']][REV] + ' %s\n' % true_label)
        elif expr['Right']['Type'] in ('BoolLiteral', 'NumLiteral') and not expr['Right']['Value']:
            self.emit_expr(expr['Left'])
            self.emit(RELATIONAL_MNEMONICS[expr['Op']['Op']][NORM] + ' %s\n' % true_label)
        else:
            self.emit_expr(expr['Left'])
            self.emit_expr(expr['Right'])
            if expr['Right']['EvalType'] in ('int', 'boolean'):
                self.emit(RELATIONAL_MNEMONICS[expr['Op']['Op']][BIN_NORM] + ' %s\n' % true_label)
            elif expr['Right']['EvalType'] == 'string':
                self.emit('invokevirtual java/lang/String/equals(Ljava/lang/String)B')
                if not jump_if_true and not jump_if_false:
                    return
                self.emit('if_icmpge %s' % true_label)

        if jump_if_false and jump_if_false != next_label:
            self.emit('goto %d\n' % jump_if_false)
        elif not jump_if_false:
            self.emit('iconst_0\n')
        if not jump_if_true:
            self.emit(true_label + '\n')
            self.emit('iconst_1\n')


    def emit_expr(self, expr, jump_if_true=None, jump_if_false=None, next_label=None):
        if expr['Type'] == 'NumLiteral':
            self.emit('iconst%c%d\n' % ('_' if expr['Value'] < OPTIMIZED_LIMIT else ' ',
                expr['Value']))
        elif expr['Type'] == 'BoolLiteral':
            if expr['Value'] and jump_if_true and next_label != jump_if_true:
                self.emit('goto %s\n' % jump_if_true)
            elif not expr['Value'] and jump_if_false and next_label != jump_if_false:
                self.emit('goto %s\n' % jump_if_false)
            else:
                self.emit('iconst%c%d\n' % ('_' if expr['Value'] < OPTIMIZED_LIMIT else ' ',
                    1 if expr['Value'] else 0))
        elif expr['Type'] == 'StrLiteral':
            self.emit('ldc "%s"\n' % expr['Value'])

        elif expr['Type'] == 'UnaryOp':
            self.emit_expr(expr['Arg'])
            if expr['Op']['Op'] == '-':
                self.emit("ineg\n")
            else:
                # TODO: negation
                pass
        elif expr['Type'] == 'BinaryOp':
            if expr['Op']['MetaType'] == 'ArithmOp':
                self.emit_expr_arithm(expr)
            elif expr['Op']['MetaType'] == 'LogOp':
                self.emit_expr_log(expr, jump_if_true, jump_if_false, next_label)
            else:
                self.emit_expr_rel(expr, jump_if_true, jump_if_false, next_label)

        elif expr['Type'] == 'Var':
            self.emit('%cload%c%d\n' % self.get_var_info(expr['Name']))
        elif expr['Type'] == 'FunCall':
            return self.emit_funcall(expr)


    def emit_funcall(self, expr):
        for arg in expr['ListArg']:
            self.emit('%cload%c%d\n' % self.get_var_info(expr['Name']))
        self.emit('invokestatic %s %c\n' % (expr['Name'],
            self.get_jvm_type(self.__functions(expr['Name'])['LatteType']['TypeName'])))


    def emit_var_decl(self, stmt):
        prefix = 'i' if stmt['LatteType']['TypeName'] in ('int', 'boolean') else 'a'
        for item in stmt['Items']:
            underscore_optimization = '_' if self.__locals_counter < OPTIMIZED_LIMIT else ' '
            if item['Assigned']:
                self.emit_expr(item['Assigned'])
            else:
                self.emit('%cload%c%d\n' % (prefix, underscore_optimization, 0))
            self.emit('%cstore%c%d\n' % (prefix, underscore_optimization,
                self.__locals_counter))
            self.__environments[-1][item['Name']] = {'LatteType': item['LatteType'], 'JVMVarNo': self.__locals_counter}
            self.__locals_counter += 1


    def emit_while_loop(self, stmt):
        begin_label = 'LWHILE_BEGIN%d\n' % self.__label_counter
        self.emit('goto LWHILE_END%d\n' % self.__label_counter)
        self.emit(begin_label)
        self.emit_stmt(stmt['Stmt'])
        self.emit('LWHILE_END%d\n' % self.__label_counter)
        self.emit_expr(stmt['Condition'], begin_label)
        self.emit_jump(stmt, 'LWHILE_BEGIN%d' % self.__label_counter)
        self.__label_counter += 1


    def emit_if_stmt(self, stmt):
        true_label = 'LIFTRUE%d' % self.__label_counter
        false_label = 'LIFFALSE%d' % self.__label_counter
        self.emit_expr(stmt['Condition'], true_label, false_label, false_label)
        self.emit(false_label + '\n')
        if stmt['Type'] == 'IfElseStmt':
            self.emit_stmt(stmt['Stmt2'])
        self.emit('goto LIFEND%d\n' % self.__label_counter)
        self.emit(true_label + '\n')
        self.emit(stmt['Stmt' if stmt['Type'] == 'IfStmt' else 'Stmt1'])
        self.emit('LIFEND:\n')
        self.__label_counter += 1


    def emit_assign(self, stmt):
        self.emit_expr(stmt['Expr'])
        self.emit('%cstore%c%d\n' % self.get_var_info(expr['Name']))


    def emit_inc_dec(self, stmt):
        self.emit('iinc %d %d\n', get_var(self.__environments, expr['Name'])['JVMVarNo'],
            1 if stmt['Op'] == '++' else -1)


    def emit_ret(self, stmt):
        if stmt['Expr']:
            self.emit_expr(stmt['Expr'])
            self.emit('%creturn' % 'i' if stmt['Expr']['EvalType'] in ('int', 'boolean') else 'a')
        else:
            self.emit('return\n')


    def emit_stmt(self, stmt):
        if stmt['Type'] == 'VariableDecl':
            self.emit_var_decl(stmt)
        elif stmt['Type'] == 'WhileLoop':
            self.emit_while_loop(stmt)
        elif stmt['Type'] in ('IfStmt', 'IfElseStmt'):
            self.emit_if_stmt(stmt)
        elif stmt['Type'] == 'Expr':
            self.emit_expr(stmt)
        elif stmt['Type'] == 'IncDec':
            self.emit_inc_dec(stmt)
        elif stmt['Type'] == 'Assignment':
            self.emit_assign(stmt)
        elif stmt['Type'] == 'Return':
            self.emit_ret(stmt)


    def push_env(self, function = None):
        self.__environments.append({})
        param_counter = 0
        if function:
            for param in function['ListArg']:
                self.__environments[-1][param['Name']] = {'LatteType': param['LatteType'],
                    'JVMVarNo': param_counter}
                param_counter += 1


    def get_var_info(self, name):
        JVMVar = get_var(self.__environments, name)
        prefix = 'i' if JVMVar['LatteType']['TypeName'] in ('int', 'boolean') else 'a'
        return  prefix, '_' if JVMVar['JVMVarNo'] < OPTIMIZED_LIMIT else ' ', JVMVar['JVMVarNo']


    def get_argument_list(self, function):
        return ''.join(self.get_jvm_type(arg['LatteType']['TypeName']) for arg in function['ListArg'])


    def get_jvm_type(self, typeName):
        if typeName == 'void':
            return 'V'
        elif typeName in ('int', 'boolean'):
            return 'I'
        elif typeName == 'string':
            return 'Ljava/lang/String;'


    def generate_jvm(self):
        for function in self.__syntax_tree:
            self.current_function = ['.method public static %s(%s)%s\n' %(function['Name'],
                    self.get_argument_list(function), self.get_jvm_type(function['LatteType']['TypeName']))]
            # need to add limit stack and limit locals, but this can be done after
            for stmt in function['Body']['Stmts']:
                self.emit_stmt(stmt)
            self.__jasmin_strings.append(''.join(self.current_function))
            self.__locals_counter = 0
        return ''.join(self.__jasmin_strings)

