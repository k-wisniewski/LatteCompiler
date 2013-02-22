from shared.utils import get_var, MAIN_MANGLING
OPTIMIZED_LIMIT = 4
BIPUSH_LIMIT    = 1 << 7
SIPUSH_LIMIT    = 1 << 15


RELATIONAL_MNEMONICS = {
#   OP       NORM    NEG     REV     NEG_REV BIN_NORM    BIN_NEG
    '<'  : ('iflt', 'ifge', 'ifgt', 'ifle', 'if_icmplt', 'if_icmpge'),
    '<=' : ('ifle', 'ifgt', 'ifge', 'iflt', 'if_icmple', 'if_icmpgt'),
    '>'  : ('ifgt', 'ifle', 'iflt', 'ifge', 'if_icmpgt', 'if_icmple'),
    '>=' : ('ifge', 'iflt', 'ifle', 'ifgt', 'if_icmpge', 'if_icmplt'),
    '==' : ('ifeq', 'ifne', 'ifeq', 'ifne', 'if_icmpeq', 'if_icmpne'),
    '!=' : ('ifne', 'ifeq', 'ifne', 'ifeq', 'if_icmpne', 'if_icmpeq')
}

NORM        = 0
NEG         = 1
REV         = 2
NEG_REV     = 3
BIN_NORM    = 4
BIN_NEG     = 5

DEFAULT_CLASS_NAME  = 'DefaultClass'

class JVM_Backend:
    def __init__(self, syntax_tree, functions, class_name=None):
        self.__syntax_tree = syntax_tree
        self.__class_name = DEFAULT_CLASS_NAME if not class_name else class_name
        self.__jasmin_strings = ['.class public %s\n'
            '.super java/lang/Object\n' % self.__class_name]
        self.__locals_counter = 1
        self.__stack_limit = 0
        self.__label_counter = 0
        self.__bool_exp_generated = False
        self.__functions = functions
        self.__environments = []


    def emit(self, text):
        self.current_function.append(text)


    def emit_expr_string_concat(self, expr):
        self.emit('new java/lang/StringBuilder\n')
        self.emit('dup\n')
        self.emit_expr(expr['Left'])
        self.emit('invokespecial java/lang/StringBuilder/<init>(Ljava/lang/String;)V\n')
        self.emit_expr(expr['Right'])
        self.emit('invokevirtual java/lang/StringBuilder.append(Ljava/lang/String;)Ljava/lang/StringBuilder;\n')
        self.emit('invokevirtual java/lang/StringBuilder.toString()Ljava/lang/String;\n')


    def emit_expr_arithm(self, expr):
        if expr['EvalType'] == 'string' and expr['Op']['Op'] == '+':
            self.emit_expr_string_concat(expr)
        else:
            self.emit_expr(expr['Left'])
            self.emit_expr(expr['Right'])
            if expr['Op']['Op'] == '+':
                self.emit('iadd\n')
            elif expr['Op']['Op'] == '-':
                self.emit('isub\n')
            elif expr['Op']['Op'] == '*':
                self.emit('imul\n')
            elif expr['Op']['Op'] == '/':
                self.emit('idiv\n')
            elif expr['Op']['Op'] == '%':
                self.emit('irem\n')


    def emit_expr_log(self, expr, jump_if_true, jump_if_false, next_label, negate):
        self.__label_counter += 1
        local_false_label = 'LFALSE%d' % self.__label_counter
        local_true_label = 'LTRUE%d' % self.__label_counter
        false_label = jump_if_false if jump_if_false else local_false_label
        true_label = jump_if_true if jump_if_true else local_true_label
        end_label = 'LEND%d' % self.__label_counter
        if (not negate and expr['Op']['Op'] == '&&') or (negate and expr['Op']['Op'] == '||'):
            next_condition_label = local_true_label
            self.emit_expr(expr['Left'], next_condition_label, false_label, next_condition_label, negate)
            self.emit(next_condition_label + ':\n')

            self.emit_expr(expr['Right'], jump_if_true, false_label, next_label, negate)
            if not jump_if_true and not jump_if_false:
                if not self.__bool_exp_generated:
                    self.emit('iconst_1\n')
                else:
                    self.__bool_exp_generated = False
                self.emit('goto %s\n' % end_label)
            if not jump_if_false:
                self.emit(local_false_label + ':\n')
            if not jump_if_true and not jump_if_false:
                self.emit('iconst_0\n')
                self.emit(end_label + ':\n')
                self.emit('nop\n')

        elif (not negate and expr['Op']['Op'] == '||') or (negate and expr['Op']['Op'] == '&&'):
            next_condition_label = local_false_label
            self.emit_expr(expr['Left'], true_label, next_condition_label, next_condition_label, negate)
            self.emit(next_condition_label + ':\n')
            self.emit_expr(expr['Right'], true_label, jump_if_false, next_label, negate)
            if not jump_if_true and not jump_if_false:
                self.emit('iconst_0\n')
                self.emit('goto %s\n' % end_label)
            if not jump_if_true:
                self.emit(local_true_label + ':\n')
            if not jump_if_true and not jump_if_false:
                self.emit('iconst_1\n')
                self.emit(end_label + ':\n')
                self.emit('nop\n')


    def emit_expr_rel(self, expr, jump_if_true, jump_if_false, next_label, negate):
        self.__label_counter += 1
        true_label = jump_if_true if jump_if_true else 'LTRUE%d' % self.__label_counter
        end_label = 'LEND%d' % self.__label_counter
        if expr['Left']['Type'] in ('BoolLiteral', 'NumLiteral') and not expr['Left']['Value']:
            self.emit_expr(expr['Right'])
            self.emit(RELATIONAL_MNEMONICS[expr['Op']['Op']][NEG_REV if negate else REV] +
                ' %s\n' % true_label)
        elif expr['Right']['Type'] in ('BoolLiteral', 'NumLiteral') and  not expr['Right']['Value']:
            self.emit_expr(expr['Left'])
            self.emit(RELATIONAL_MNEMONICS[expr['Op']['Op']][NEG if negate else NORM] +
                ' %s\n' % true_label)
        else:
            self.emit_expr(expr['Left'])
            self.emit_expr(expr['Right'])
            if expr['Right']['EvalType'] in ('int', 'boolean'):
                self.emit(RELATIONAL_MNEMONICS[expr['Op']['Op']][BIN_NEG if negate else BIN_NORM] +
                    ' %s\n' % true_label)
            elif expr['Right']['EvalType'] == 'string':
                self.emit('invokevirtual java/lang/String/equals(Ljava/lang/Object;)Z\n')
                if not jump_if_true and not jump_if_false:
                    return
                self.emit(('ifgt' if not negate else 'ifle') + ' %s\n' % true_label)

        if jump_if_false and jump_if_false != next_label:
            self.emit('goto %s\n' % jump_if_false)
        elif not jump_if_false and not jump_if_true:
            self.emit('iconst_0\n')
            self.emit('goto %s\n' % end_label)
        if not jump_if_true:
            self.emit(true_label + ':\n')
        if not jump_if_false and not jump_if_true:
            self.emit('iconst_1\n')
            self.emit(end_label + ':\n')
            self.emit('nop\n')


    def emit_expr_num(self, expr):
        if expr['Value'] < OPTIMIZED_LIMIT and expr['Value'] >= 0:
            self.emit('iconst_%d\n' % expr['Value'])
        elif expr['Value'] >= -BIPUSH_LIMIT and expr['Value'] < BIPUSH_LIMIT:
            self.emit('bipush %d\n' % expr['Value'])
        elif expr['Value'] >= -SIPUSH_LIMIT and expr['Value'] < SIPUSH_LIMIT:
            self.emit('sipush %d\n' % expr['Value'])
        else:
            self.emit('ldc %d\n' % expr['Value'])


    def emit_expr_bool(self, expr, jump_if_true, jump_if_false, next_label, negate):
        if expr['Value'] != negate and jump_if_true and next_label != jump_if_true:
            self.emit('goto %s\n' % jump_if_true)
        elif not expr['Value'] and jump_if_false and next_label != jump_if_false:
            self.emit('goto %s\n' % jump_if_false)
        else:
            self.__bool_exp_generated = True
            self.emit('iconst_%d\n' % ((0 if negate else 1) if expr['Value'] else (1 if negate else 0)))

    def emit_expr_unary(self, expr, jump_if_true, jump_if_false, next_label, negate):
        if expr['Op']['Op'] == '-':
            self.emit_expr(expr['Arg'])
            self.emit("ineg\n")
        else:
            self.emit_expr(expr['Arg'], jump_if_true, jump_if_false, next_label, not negate)


    def emit_expr_var(self, expr, jump_if_true, jump_if_false, next_label, negate):
        self.emit('%cload%c%d\n' % self.get_var_info(expr))
        if jump_if_true:
            self.emit(('ifeq' if negate else 'ifgt') + ' %s\n' % jump_if_true)
            if jump_if_false:
                self.emit('goto %s\n' % jump_if_false)
        elif jump_if_false:
            self.__label_counter += 1
            self.emit(('ifeq' if negate else 'ifgt') + ' LTRUE%d\n' % self.__label_counter)
            self.emit('goto %s\n' % jump_if_false)
            self.emit('LTRUE%d:\n' % self.__label_counter)


    def emit_expr_funcall(self, expr, jump_if_true, jump_if_false, next_label, negate):
        self.emit('aload_0\n')
        for arg in expr['ListArg']:
            self.emit_expr(arg)
        if expr['Name'] in ('printInt', 'printString', 'error', 'readInt', 'readString'):
            self.emit('invokevirtual Runtime/%s(%s)%s\n' % (expr['Name'],
            self.get_argument_list(self.__functions[expr['Name']], runtime=True),
            self.get_jvm_type(self.__functions[expr['Name']]['LatteType']['TypeName'])))

        else:
            self.emit('invokestatic %s/%s(%s)%s\n' % (self.__class_name, expr['Name'],
                self.get_argument_list(self.__functions[expr['Name']]),
                self.get_jvm_type(self.__functions[expr['Name']]['LatteType']['TypeName'])))
        if jump_if_true:
            self.emit(('ifeq' if negate else 'ifgt') + ' %s\n' % jump_if_true)
            if jump_if_false:
                self.emit('goto %s\n' % jump_if_false)
        elif jump_if_false:
            self.__label_counter += 1
            self.emit(('ifeq' if negate else 'ifgt') + ' LTRUE%d\n' % self.__label_counter)
            self.emit('goto %s\n' % jump_if_false)
            self.emit('LTRUE%d:\n' % self.__label_counter)


    def emit_expr(self, expr, jump_if_true=None, jump_if_false=None, next_label=None, negate=False):
        if expr['Type'] == 'NumLiteral':
            self.emit_expr_num(expr)
        elif expr['Type'] == 'BoolLiteral':
            self.emit_expr_bool(expr, jump_if_true, jump_if_false, next_label, negate)
        elif expr['Type'] == 'StrLiteral':
            self.emit('ldc "%s"\n' % expr['Value'])
        elif expr['Type'] == 'UnaryOp':
            self.emit_expr_unary(expr, jump_if_true, jump_if_false, next_label, negate)
        elif expr['Type'] == 'BinaryOp':
            if expr['Op']['MetaType'] == 'ArithmOp':
                self.emit_expr_arithm(expr)
            elif expr['Op']['MetaType'] == 'LogOp':
                self.emit_expr_log(expr, jump_if_true, jump_if_false, next_label, negate)
            else:
                self.emit_expr_rel(expr, jump_if_true, jump_if_false, next_label, negate)

        elif expr['Type'] == 'Var':
            self.emit_expr_var(expr, jump_if_true, jump_if_false, next_label, negate)
        elif expr['Type'] == 'FunCall':
            self.emit_expr_funcall(expr, jump_if_true, jump_if_false, next_label, negate)


    def emit_var_decl(self, stmt):
        prefix = 'i' if stmt['LatteType']['TypeName'] in ('int', 'boolean') else 'a'
        for item in stmt['Items']:
            underscore_optimization = '_' if self.__locals_counter < OPTIMIZED_LIMIT else ' '
            if item['Assigned']:
                self.emit_expr(item['Assigned'])
            elif stmt['LatteType']['TypeName'] in ('int', 'boolean'):
                self.emit('iconst_0\n')
            else:
                self.emit('ldc ""\n')
            self.emit('%cstore%c%d\n' % (prefix, underscore_optimization,
                self.__locals_counter))
            self.__environments[-1][item['Name']] = {'LatteType': item['LatteType'],
                    'EvalType': item['LatteType']['TypeName'], 'JVMVarNo': self.__locals_counter}
            self.__locals_counter += 1


    def emit_while_loop(self, stmt):
        self.__label_counter += 1
        begin_label = 'LWHILE_BEGIN%d' % self.__label_counter
        end_label = 'LWHILE_END%d' % self.__label_counter
        self.emit('goto %s\n' % end_label)
        self.emit(begin_label + ':\n')
        self.emit_stmt(stmt['Stmt'])
        self.emit(end_label + ':\n')
        self.emit_expr(stmt['Condition'], begin_label)


    def emit_if_stmt(self, stmt):
        self.__label_counter += 1
        # TODO: optimize goto after return
        true_label = 'LIFTRUE%d' % self.__label_counter
        false_label = 'LIFFALSE%d' % self.__label_counter
        end_label = 'LIFEND%d' % self.__label_counter
        self.emit_expr(stmt['Condition'], true_label, false_label, false_label)
        self.emit(false_label + ':\n')
        if stmt['Type'] == 'IfElseStmt':
            self.emit_stmt(stmt['Stmt2'])
        self.emit('goto %s\n' % end_label)
        self.emit(true_label + ':\n')
        self.emit_stmt(stmt['Stmt' if stmt['Type'] == 'IfStmt' else 'Stmt1'])
        self.emit(end_label + ':\n')
        self.emit('nop\n')


    def emit_assign(self, stmt):
        self.emit_expr(stmt['Expr'])
        self.emit('%cstore%c%d\n' % self.get_var_info(stmt))


    def emit_inc_dec(self, stmt):
        self.emit('%cload%c%d\n' % self.get_var_info(stmt))
        self.emit('iinc %d %d\n' % (get_var(self.__environments, stmt)['JVMVarNo'],
            1 if stmt['Op'] == '++' else -1))
        self.emit('pop\n')


    def emit_ret(self, stmt):
        if stmt['Expr']:
            self.emit_expr(stmt['Expr'])
            self.emit('%creturn\n' % ('i' if stmt['Expr']['EvalType'] in ('int', 'boolean') else 'a'))
        else:
            self.void_ret_handled = True
            self.emit('return\n')

    def emit_block(self, stmt):
        self.__push_env()
        for internal_stmt in stmt['Stmts']:
            self.emit_stmt(internal_stmt)
        self.__pop_env()

    def emit_stmt(self, stmt):
        if stmt['Type'] == 'VariableDecl':
            self.emit_var_decl(stmt)
        elif stmt['Type'] == 'WhileLoop':
            self.emit_while_loop(stmt)
        elif stmt['Type'] in ('IfStmt', 'IfElseStmt'):
            self.emit_if_stmt(stmt)
        elif stmt['Type'] == 'Expr':
            self.emit_expr(stmt['Expr'])
        elif stmt['Type'] == 'IncDec':
            self.emit_inc_dec(stmt)
        elif stmt['Type'] == 'Assignment':
            self.emit_assign(stmt)
        elif stmt['Type'] == 'Return':
            self.emit_ret(stmt)
        elif stmt['Type'] == 'Block':
            self.emit_block(stmt)

    def __push_env(self, function = None):
        self.__environments.append({})
        param_counter = 1
        if function:
            for param in function['ListArg']:
                self.__environments[-1][param['Name']] = {'LatteType': param['LatteType'],
                    'JVMVarNo': param_counter}
                self.__locals_counter += 1
                param_counter += 1


    def __pop_env(self):
        self.__environments.pop()


    def get_var_info(self, var):
        JVMVar = get_var(self.__environments, var)
        prefix = 'i' if JVMVar['LatteType']['TypeName'] in ('int', 'boolean') else 'a'
        return  prefix, '_' if JVMVar['JVMVarNo'] < OPTIMIZED_LIMIT else ' ', JVMVar['JVMVarNo']


    def get_argument_list(self, function, runtime=False):
        if not runtime:
            return 'LRuntime;' + ''.join(self.get_jvm_type(arg['LatteType']['TypeName']) for arg in function['ListArg'])
        else:
            return ''.join(self.get_jvm_type(arg['LatteType']['TypeName']) for arg in function['ListArg'])


    def get_jvm_type(self, typeName):
        if typeName == 'void':
            return 'V'
        elif typeName in ('int', 'boolean'):
            return 'I'
        elif typeName == 'string':
            return 'Ljava/lang/String;'


    def generate_jvm(self):
        self.__jasmin_strings.append('.method public static main([Ljava/lang/String;)V\n'
                '.limit locals 100\n'
                '.limit stack 100\n'
                'new Runtime\n'
                'dup\n'
                'invokespecial Runtime/<init>()V\n'
                'invokestatic %s/main_%d(LRuntime;)I\n'
                'return\n'
                '.end method\n' % (self.__class_name, MAIN_MANGLING))
        for function in self.__syntax_tree:
            self.current_function = ['.method public static %s(%s)%s\n' %(function['Name'],
                    self.get_argument_list(function), self.get_jvm_type(function['LatteType']['TypeName']))]
            self.current_function.append('.limit locals 100\n')
            self.current_function.append('.limit stack 100\n')
            self.__push_env(function)
            self.void_ret_handled = False
            for stmt in function['Body']['Stmts']:
                self.emit_stmt(stmt)
            if function['LatteType']['TypeName'] == 'void' and not self.void_ret_handled:
                self.emit('return\n')
            self.emit('.end method\n')
            #self.current_function[1] = self.current_function[1] + "%d\n" % self.__locals_counter
            self.__jasmin_strings.append(''.join(self.current_function))
            self.__locals_counter = 1
            self.__pop_env()
        return ''.join(self.__jasmin_strings)

