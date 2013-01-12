from llvm.core    import *
from shared.utils import get_var

SIZEOF_INT = 32
SIZEOF_BYTE = 8

RELATIONAL_METADATA = {
    '<': (ICMP_SLT, 'LTTMP'),
    '>': (ICMP_SGT, 'GTTMP'),
    '<=': (ICMP_SLE, 'GETMP'),
    '>=': (ICMP_SGE, 'LETMP'),
    '==': (ICMP_EQ, 'EQTMP'),
    '!=': (ICMP_NE, 'NETMP')
}

PRED = 0
NAME = 1

TYPE_OBJS = {
    'int': Type.int(SIZEOF_INT),
    'boolean': Type.int(SIZEOF_BYTE),
    'string': Type.pointer(Type.int(SIZEOF_BYTE)),
    'void': Type.void()
}

class LLVM_Backend:

    def __init__(self, syntax_tree, functions, module_name):
        self.__module = Module.new(module_name)
        self.__llvm_builder = None
        self.__syntax_tree = syntax_tree
        self.__functions = functions
        self.__environments = []


    def gen_expr_arithm(self, expr, left, right):
        #if expr['EvalType'] == 'string' and expr['Op']['Op'] == '+':
        #    self.gen_expr_string_concat(expr)
        #else:
            if expr['Op']['Op'] == '+':
                return self.__llvm_builder.add(left, right, 'addtmp')
            elif expr['Op']['Op'] == '-':
                return self.__llvm_builder.sub(left, right, 'subtmp')
            elif expr['Op']['Op'] == '*':
                return self.__llvm_builder.mul(left, right, 'multmp')
            elif expr['Op']['Op'] == '/':
                return self.__llvm_builder.div(left, right, 'divtmp')
            elif expr['Op']['Op'] == '%':
                return self.__llvm_builder.srem(left, right, 'modtmp')


    def gen_expr_rel(self, expr, left, right):
        if expr['Left']['EvalType'] in ('int', 'boolean'):
            return self.__llvm_builder.icmp(RELATIONAL_METADATA[expr['Op']['Op']][PRED],
                    left, right, RELATIONAL_METADATA[expr['Op']['Op']][NAME])
        else:
            # TODO: string comparison
            pass


    def gen_expr_log(self, expr, left, right):
        if expr['Op']['Op'] == '&&':
            return self.__llvm_builder.and_(left, right, 'andtmp')
        elif expr['Op']['Op'] == '||':
            return self.__llvm_builder.or_(left, right, 'ortmp')


    def gen_expr_unary(self, expr):
        if expr['Op']['Op'] == '!':
            return self.__llvm_builder.not_(self.gen_expr(expr['Arg']), 'andtmp')
        if expr['Op']['Op'] == '-':
            p = self.gen_expr(expr['Arg'])
            return self.__llvm_builder.sub(Constant.int(Type.int(), 0),
                    p, 'andtmp')


    def gen_expr_var(self, expr):
        return self.__llvm_builder.load(get_var(self.__environments, expr))


    def gen_expr_funcall(self, expr):
        return self.__llvm_builder.call(self.__module.get_function_named(expr['Name']),
                [self.gen_expr(arg) for arg in expr['ListArg']], 'calltmp')


    def gen_expr(self, expr):
        if expr['Type'] == 'NumLiteral':
            return Constant.int(Type.int(), expr['Value'])
        elif expr['Type'] == 'BoolLiteral':
            return Constant.int(Type.int(SIZEOF_BYTE), expr['Value'])
        elif expr['Type'] == 'StrLiteral':
            return Constant.array(Type.int(SIZEOF_BYTE), len(expr['Value']))
        elif expr['Type'] == 'UnaryOp':
            self.gen_expr_unary(expr)
        elif expr['Type'] == 'BinaryOp':
            left = self.gen_expr(expr['Left'])
            right = self.gen_expr(expr['Right'])
            if expr['Op']['MetaType'] == 'ArithmOp':
                return self.gen_expr_arithm(expr, left, right)
            elif expr['Op']['MetaType'] == 'LogOp':
                return self.gen_expr_log(expr, left, right)
            else:
                return self.gen_expr_rel(expr, left, right)

        elif expr['Type'] == 'Var':
            return self.gen_expr_var(expr)
        elif expr['Type'] == 'FunCall':
            return self.gen_expr_funcall(expr)


    def gen_if_stmt(self, stmt):
        condition = self.gen_expr(stmt['Condition'])
        function = self.__llvm_builder.basic_block.function
        then_block = function.append_basic_block('then')
        merge_block = function.append_basic_block('ifcond')
        if stmt['Type'] == 'IfElseStmt':
            else_block = function.append_basic_block('else')
            self.__llvm_builder.cbranch(condition, then_block, else_block)
            self.__llvm_builder.position_at_end(then_block)
            self.gen_stmt(stmt['Stmt1'])
            self.__llvm_builder.branch(merge_block)
            self.__llvm_builder.position_at_end(else_block)
            self.gen_stmt(stmt['Stmt2'])
            self.__llvm_builder.branch(merge_block)
        else:
            self.__llvm_builder.cbranch(condition, then_block, merge_block)
            self.__llvm_builder.position_at_end(then_block)
            self.gen_stmt(stmt['Stmt'])
            self.__llvm_builder.branch(merge_block)
        self.__llvm_builder.position_at_end(merge_block)


    def gen_var_decl(self, stmt):
        for item in stmt['Items']:
            var_val = Constant.int(Type.int(), 0)
            if item['Assigned']:
                var_val = self.gen_expr(item['Assigned'])
            alloca = self.alloc_in_entry_block(TYPE_OBJS[stmt['LatteType']['TypeName']],
                    stmt['LatteType']['TypeName'])
            self.__llvm_builder.store(var_val, alloca)
            self.__environments[-1][item['Name']] = alloca


    def gen_while_loop(self, stmt):
        function = self.__llvm_builder.basic_block.function
        cond_block = function.append_basic_block('while_cond')
        self.__llvm_builder.branch(cond_block)
        loop_block = function.append_basic_block('loop')
        merge_block = function.append_basic_block('while_merge')
        self.__llvm_builder.position_at_end(cond_block)
        condition = self.gen_expr(stmt['Condition'])
        self.__llvm_builder.cbranch(condition, loop_block, merge_block)
        self.__llvm_builder.position_at_end(loop_block)
        self.gen_stmt(stmt['Stmt'])
        self.__llvm_builder.branch(cond_block)
        self.__llvm_builder.position_at_end(merge_block)


    def gen_assign(self, stmt):
        value = self.gen_expr(stmt['Expr'])
        self.__llvm_builder.store(value, get_var(self.__environments, stmt))


    def gen_ret(self, stmt):
        self.__current_function_returns = True
        if stmt['Expr']:
            self.__llvm_builder.ret(self.gen_expr(stmt['Expr']))
        else:
            self.__llvm_builder.ret_void()


    def gen_inc_dec(self, stmt):
        var = self.__llvm_builder.load(get_var(self.__environments, stmt))
        if stmt['Op'] == '++':
            result = self.__llvm_builder.add(var, Constant.int(Type.int(), 1))
        else:
            result = self.__llvm_builder.sub(var, Constant.int(Type.int(), 1))
        self.__llvm_builder.store(result,get_var(self.__environments, stmt))


    def gen_block(self, stmt):
        self.__push_env()
        for internal_stmt in stmt['Stmts']:
            self.gen_stmt(internal_stmt)
        self.__pop_env()


    def gen_stmt(self, stmt):
        if stmt['Type'] == 'VariableDecl':
            self.gen_var_decl(stmt)
        elif stmt['Type'] == 'WhileLoop':
            self.gen_while_loop(stmt)
        if stmt['Type'] in ('IfStmt', 'IfElseStmt'):
            self.gen_if_stmt(stmt)
        elif stmt['Type'] == 'Expr':
            self.gen_expr(stmt['Expr'])
        elif stmt['Type'] == 'IncDec':
            self.gen_inc_dec(stmt)
        elif stmt['Type'] == 'Assignment':
            self.gen_assign(stmt)
        elif stmt['Type'] == 'Return':
            self.gen_ret(stmt)
        elif stmt['Type'] == 'Block':
            self.gen_block(stmt)


    def get_function_type(self):
        return Type.function(TYPE_OBJS[self.current_function_ast['LatteType']['TypeName']],
            tuple(TYPE_OBJS[arg['LatteType']['TypeName']]
                for arg in self.current_function_ast['ListArg']), False)


    def __push_env(self):
        self.__environments.append({})
        param_counter = 1


    def __pop_env(self):
        self.__environments.pop()


    def alloc_in_entry_block(self, var_name, type_):
        entry = self.current_function_llvm.get_entry_basic_block()
        builder = Builder.new(entry)
        builder.position_at_beginning(entry)
        return builder.alloca(var_name)


    def generate_llvm(self):
        for function in self.__syntax_tree:
            self.__current_function_returns = False
            self.__push_env()
            self.current_function_ast = function
            self.current_function_llvm = Function.new(self.__module, self.get_function_type(), function['Name'])
            self.__llvm_builder = Builder.new(self.current_function_llvm.append_basic_block('entry'))
            for arg, arg_passed in zip(self.current_function_llvm.args, function['ListArg']):
                arg.name = arg_passed['Name']
                print "dupa"
                alloca = self.alloc_in_entry_block(TYPE_OBJS[arg_passed['LatteType']['TypeName']], arg.name)
                self.__llvm_builder.store(arg, alloca)
                self.__environments[-1][arg_passed['Name']] = alloca
            print(len(self.current_function_llvm.args))
            for stmt in function['Body']['Stmts']:
                self.gen_stmt(stmt)
            if not self.__current_function_returns and function['LatteType']['TypeName']:
                self.__llvm_builder.ret_void()
            self.current_function_llvm.verify()
            self.__pop_env()
            print self.__llvm_builder.basic_block.function
