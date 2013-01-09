from llvm.core    import *

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

class LLVM_Backend:

    def __init__(self, syntax_tree, functions):
        self.__module = Module.new(module_name)
        self.__llvm_builder = None
        self.__syntax_tree = syntax_tree
        self.__functions = functions
        self.__environments = []
        t_byte = Type.int(SIZEOF_BYTE)
        self.__type_objs = {
                'int': Type.int(SIZEOF_INT),
                'boolean': t_byte,
                'string': Type.pointer(t_byte),
                'void': Type.void()
            }


    def gen_expr_arithm(self, expr):
        #if expr['EvalType'] == 'string' and expr['Op']['Op'] == '+':
        #    self.gen_expr_string_concat(expr)
        #else:
            left = self.gen_expr(expr['Left'])
            right = self.gen_expr(expr['Right'])
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

    def gen_expr_rel(self, expr):
        left = self.gen_expr(expr['Left'])
        right = self.gen_expr(expr['Right'])
        if expr['Left']['EvalType'] in ('int', 'boolean'):
            return self.__llvm_builder.icmp(RELOP_METADATA[expr['Op']['Op'][PRED]],
                    left, right, RELOP_METADATA[expr['Op']['Op']][NAME])
        else:
            # TODO: string comparison
            pass

    def gen_expr(self, expr):
        if expr['Type'] == 'NumLiteral':
            return Constant.int(Type.int(), expr['Value'])
        elif expr['Type'] == 'BoolLiteral':
            return Constant.int(Type.int(8), expr['Value'])
        elif expr['Type'] == 'StrLiteral':
            return Constant.array(Type.int(8), len(expr['Value']))
            self.gen('ldc "%s"\n' % expr['Value'])
        elif expr['Type'] == 'UnaryOp':
            self.gen_expr_unary(expr, jump_if_true, jump_if_false, next_label, negate)
        elif expr['Type'] == 'BinaryOp':
            if expr['Op']['MetaType'] == 'ArithmOp':
                return self.gen_expr_arithm(expr)
            elif expr['Op']['MetaType'] == 'LogOp':
                self.gen_expr_log(expr, jump_if_true, jump_if_false, next_label, negate)
            else:
                return gen_expr_rel(expr)
                return self.__llvm_builder.icmp(RELATIONAL)
                self.gen_expr_rel(expr, jump_if_true, jump_if_false, next_label, negate)

        elif expr['Type'] == 'Var':
            self.gen_expr_var(expr, jump_if_true, jump_if_false, next_label, negate)
        elif expr['Type'] == 'FunCall':
            self.gen_expr_funcall(expr, jump_if_true, jump_if_false, next_label, negate)



    def gen_stmt(self, stmt):
        if stmt['Type'] == 'VariableDecl':
            self.gen_var_decl(stmt)
        elif stmt['Type'] == 'WhileLoop':
            self.gen_while_loop(stmt)
        elif stmt['Type'] in ('IfStmt', 'IfElseStmt'):
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
        return Type.function(self.__type_objs[self.current_function_ast['LatteType']['TypeName']],
            tuple(self.__type_objs[arg['LatteType']['TypeName']]
                for arg in self.current_function_ast['ListArg']), False)



    def generate_llvm(self, module_name):
        for function in self.__syntax_tree:
            self.__llvm_builder = Builder()
            self.current_function_ast = function
            self.current_function_llvm = Function.new(self.__module, self.get_function_type(), function['Name'])
            for index, arg in enumerate(function['ListArg']):
                self.current_function_llvm.args[index].name = arg['Name']
            self.current_function_llvm.
            #self.__push_env(function)
            #for stmt in function['Body']['Stmts']:
            #    self.gen_stmt(stmt)
