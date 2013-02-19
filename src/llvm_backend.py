from llvm.core       import *
from shared.utils    import get_var, PRIMITIVES
from shared.builtins import BUILTINS_INFO

SIZEOF_INT = 32
SIZEOF_BYTE = 8
SIZEOF_BOOL = 1

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

PRIMITIVE_TYPE_OBJS = {
    'int': Type.int(SIZEOF_INT),
    'boolean': Type.int(SIZEOF_BOOL),
    'string': Type.pointer(Type.int(SIZEOF_BYTE)),
    'void': Type.void()
}

DEFAULT_CTOR_MANGLING = '_._ctor'

class LLVM_Backend:

    def __init__(self, syntax_tree, functions, class_meta, module_name):
        self.__module = Module.new(module_name)
        self.__llvm_builder = None
        self.__syntax_tree = syntax_tree
        self.__classes = [top_def for top_def in self.__syntax_tree if top_def['Type'] == 'ClassDecl']
        self.__functions = functions
        self.__llvm_functions = {}
        self.__class_meta = class_meta
        self.__current_class = None
        self.__function_envs = []
        self.__function_meta_envs = []
        self.__class_structs = {}
        self.__true_block = None
        self.__false_block = None
        self.__end_block = None
        self.__load_builtins()


    def __load_builtins(self):
        self.__llvm_functions['printInt'] =\
                Function.new(self.__module, Type.function(Type.void(), (Type.int(),)), 'printInt')
        self.__llvm_functions['printString'] =\
                Function.new(self.__module, Type.function(Type.void(),
                    (Type.pointer(Type.int(SIZEOF_BYTE)),)), 'printString')
        self.__llvm_functions['error'] =\
                Function.new(self.__module, Type.function(Type.void(), ()), 'error')
        self.__llvm_functions['readInt'] =\
                Function.new(self.__module, Type.function(Type.int(), ()), 'readInt')
        self.__llvm_functions['readString'] =\
                Function.new(self.__module, Type.function(Type.pointer(Type.int(SIZEOF_BYTE)), ()), 'readString')
        self.__memcpy = Function.intrinsic(self.__module, INTR_MEMCPY,
                [Type.pointer(Type.int(SIZEOF_BYTE)), Type.pointer(Type.int(SIZEOF_BYTE)),
                    Type.int(), Type.int(), Type.int(SIZEOF_BOOL)])
        self.__strlen = Function.new(self.__module, Type.function(Type.int(),
            (Type.pointer(Type.int(SIZEOF_BYTE)),)), 'strlen')
        self.__strcmp = Function.new(self.__module, Type.function(Type.int(),
            (Type.pointer(Type.int(SIZEOF_BYTE)), Type.pointer(Type.int(SIZEOF_BYTE)))), 'strcmp')


    def gen_expr_string_concat(self, expr, left, right):
        len_left = self.__llvm_builder.call(self.__strlen, (left,), 'lenleft')
        len_right = self.__llvm_builder.call(self.__strlen, (right,), 'lenright')
        concatenated = self.__llvm_builder.malloc_array(
                Type.int(SIZEOF_BYTE), self.__llvm_builder.add(len_left, len_right))
        self.__llvm_builder.call(self.__memcpy,
                (concatenated, left, len_left, Constant.int(Type.int(), 0),
                    Constant.int(Type.int(SIZEOF_BOOL), 0)))
        after_left = self.__llvm_builder.gep(concatenated, (len_left,))
        self.__llvm_builder.call(self.__memcpy, (after_left, right, len_right,
            Constant.int(Type.int(), 0), Constant.int(Type.int(SIZEOF_BOOL), 0)))
        return concatenated


    def gen_expr_arithm(self, expr):
        left = self.gen_expr(expr['Left'])
        right = self.gen_expr(expr['Right'])

        if expr['EvalType'] == 'string' and expr['Op']['Op'] == '+':
            return self.gen_expr_string_concat(expr, left, right)
        else:
            if expr['Op']['Op'] == '+':
                return self.__llvm_builder.add(left, right, 'addtmp')
            elif expr['Op']['Op'] == '-':
                return self.__llvm_builder.sub(left, right, 'subtmp')
            elif expr['Op']['Op'] == '*':
                return self.__llvm_builder.mul(left, right, 'multmp')
            elif expr['Op']['Op'] == '/':
                return self.__llvm_builder.sdiv(left, right, 'divtmp')
            elif expr['Op']['Op'] == '%':
                return self.__llvm_builder.srem(left, right, 'modtmp')


    def gen_expr_rel(self, expr):
        true_block = self.__true_block
        false_block = self.__false_block
        self.set_blocks_to_none()
        left = self.gen_expr(expr['Left'])
        right = self.gen_expr(expr['Right'])
        self.__true_block = true_block
        self.__false_block = false_block
        if expr['Left']['EvalType'] in ('int', 'boolean') or expr['Left']['EvalMetaType'] == 'Class':
            result = self.__llvm_builder.icmp(RELATIONAL_METADATA[expr['Op']['Op']][PRED],
                    left, right, RELATIONAL_METADATA[expr['Op']['Op']][NAME])
            if self.__false_block and self.__true_block:
                self.__llvm_builder.cbranch(result, self.__true_block, self.__false_block)
            return result
        elif expr['Left']['EvalType'] == 'string':
            result = self.__llvm_builder.call(self.__strcmp, (left, right))
            if self.__false_block and self.__true_block:
                cond = self.__llvm_builder.icmp(RELATIONAL_METADATA[expr['Op']['Op']][PRED],
                    left, right, RELATIONAL_METADATA[expr['Op']['Op']][NAME])
                self.__llvm_builder.cbranch(cond, self.__true_block, self.__false_block)
            return result


    def gen_expr_log(self, expr):
        function = self.__llvm_builder.basic_block.function
        right = None
        left = None
        if expr['Op']['Op'] == '&&':
            if self.__false_block and self.__true_block:
                true_block = self.__true_block
                self.__true_block = function.append_basic_block('right_and')
                left = self.gen_expr(expr['Left'])
                self.__llvm_builder.position_at_end(self.__true_block)
                self.__true_block = true_block
                right = self.gen_expr(expr['Right'])
            else:
                left = self.gen_expr(expr['Left'])
                right = self.gen_expr(expr['Right'])
                return self.__llvm_builder.and_(left, right, 'andtmp')

        elif expr['Op']['Op'] == '||':
            if self.__false_block and self.__true_block:
                false_block = self.__false_block
                self.__false_block = function.append_basic_block('right_or')
                left = self.gen_expr(expr['Left'])
                self.__llvm_builder.position_at_end(self.__false_block)
                self.__false_block = false_block
                right = self.gen_expr(expr['Right'])
            else:
                left = self.gen_expr(expr['Left'])
                right = self.gen_expr(expr['Right'])
                return self.__llvm_builder.or_(left, right, 'ortmp')


    def gen_expr_unary(self, expr):
        if expr['Op']['Op'] == '!':
            if self.__false_block and self.__true_block:
                true_block = self.__true_block
                false_block = self.__false_block
                self.__true_block = false_block
                self.__false_block = true_block
                self.gen_expr(expr['Arg'])
                self.__true_block = true_block
                self.__false_block = false_block
            else:
                return self.__llvm_builder.not_(self.gen_expr(expr['Arg']), 'andtmp')
        if expr['Op']['Op'] == '-':
            return self.__llvm_builder.sub(Constant.int(Type.int(), 0),
                 self.gen_expr(expr['Arg']), 'andtmp')

    def gen_expr_var(self, expr):
        var = get_var(self.__function_envs, expr, self.__class_meta, self.__current_class)
        var_meta = get_var(self.__function_meta_envs, expr, self.__class_meta, self.__current_class)
        if var_meta['LatteType']['MetaType'] != 'Array':
            result = self.__llvm_builder.load(var)
        else:
            result = var
        if self.__false_block and self.__true_block:
            self.__llvm_builder.cbranch(result, self.__true_block, self.__false_block)
        return result


    def gen_expr_funcall(self, expr):
        args = []
        for arg in expr['ListArg']:
            if arg['EvalMetaType'] != 'Array':
                args.append(self.gen_expr(arg))
            else:
                args.append(get_var(self.__function_envs, arg, self.__class_meta, self.__current_class))
        result = self.__llvm_builder.call(self.__llvm_functions[expr['Name']], args)
        if self.__false_block and self.__true_block:
            self.__llvm_builder.cbranch(result, self.__true_block, self.__false_block)
        return result


    def gen_expr_new_arr(self, expr):
        size = self.gen_expr(expr['Size'])
        malloc_type = PRIMITIVE_TYPE_OBJS[expr['EvalType']] if expr['EvalType'] in PRIMITIVES\
            else Type.pointer(self.__class_structs[expr['EvalType']])
        alloca = self.__llvm_builder.alloca(Type.struct((Type.int(), Type.pointer(malloc_type))))
        size_ptr = self.__llvm_builder.gep(alloca,
                (Constant.int(Type.int(), 0), Constant.int(Type.int(), 0)))
        arr_ptr = self.__llvm_builder.gep(alloca,
                (Constant.int(Type.int(), 0), Constant.int(Type.int(), 1)), 'arr_ptr')
        self.__llvm_builder.store(size, size_ptr)
        malloced_ptr = self.__llvm_builder.malloc_array(malloc_type, size, 'arr_ptr')
        self.__llvm_builder.store(malloced_ptr, arr_ptr)
        return alloca


    def gen_expr_new_object(self, expr):
        malloc_type = PRIMITIVE_TYPE_OBJS[expr['EvalType']] if expr['EvalType'] in PRIMITIVES\
            else self.__class_structs[expr['EvalType']]
        malloced_obj = self.__llvm_builder.malloc(malloc_type, expr['ObjectName'])
        ctor = self.__module.get_function_named(expr['EvalType'] + DEFAULT_CTOR_MANGLING)
        self.__llvm_builder.call(ctor, (malloced_obj, ))
        return malloced_obj


    def gen_expr_attribute(self, expr):
        parent_object_ptr = get_var(self.__function_envs, expr, self.__class_meta, self.__current_class)
        parent_object_meta = get_var(self.__function_meta_envs, expr, self.__class_meta, self.__current_class)
        if parent_object_meta['LatteType']['MetaType'] == 'Array' and expr['Attr'] == 'length':
            size_ptr = self.__llvm_builder.gep(parent_object_ptr,
                    (Constant.int(Type.int(), 0), Constant.int(Type.int(), 0)))
            return self.__llvm_builder.load(size_ptr)
        elif parent_object_meta['LatteType']['MetaType'] =='Class':
            parent_object_ptr = self.__llvm_builder.load(parent_object_ptr)
            parent_object_class_meta = self.__class_meta[parent_object_meta['LatteType']['TypeName']]
            index_of_attr = len(parent_object_class_meta.attributes_keys) - 1 -\
                parent_object_class_meta.attributes_keys[::-1].index(expr['Attr'])
            field_ptr = self.__llvm_builder.gep(parent_object_ptr,
                    (Constant.int(Type.int(), 0), Constant.int(Type.int(), index_of_attr)))
            return self.__llvm_builder.load(field_ptr)

            #    def gen_expr_method_call(self, expr):
            #        pass
    def gen_expr_cast(self, expr):
        casted_ptr = self.gen_expr(expr['Expr'])
        type_ = None
        if expr['ToLatteType']['MetaType'] == 'Primitive':
            type_ = PRIMITIVE_TYPE_OBJS[expr['ToLatteType']['TypeName']]
        else:
            type_ = Type.pointer(self.__class_structs[expr['ToLatteType']['TypeName']])
        return self.__llvm_builder.bitcast(casted_ptr, type_)

    def gen_expr_null(self, expr):
        return ConstantPointerNull.null(Type.pointer(Type.int(SIZEOF_BYTE)))


    def gen_expr_arr_subscript(self, expr):
        index = self.gen_expr(expr['Subscript'])
        array_struct_ptr = get_var(self.__function_envs, expr, self.__class_meta, self.__current_class)
        array_ptr = self.__llvm_builder.gep(array_struct_ptr,
            (Constant.int(Type.int(), 0), Constant.int(Type.int(), 1)))
        array = self.__llvm_builder.load(array_ptr)
        element_ptr = self.__llvm_builder.gep(array, (index, ))
        return self.__llvm_builder.load(element_ptr)


    def gen_expr(self, expr):
        if expr['Type'] == 'NumLiteral':
            return Constant.int(Type.int(), expr['Value'])
        elif expr['Type'] == 'BoolLiteral':
            if self.__true_block and self.__false_block:
                self.__llvm_builder.branch(self.__true_block\
                        if expr['Value'] else self.__false_block)
            return Constant.int(Type.int(1), expr['Value'])
        elif expr['Type'] == 'StrLiteral':
            string_const = Constant.stringz(expr['Value'])
            string = self.__module.add_global_variable(string_const.type, expr['Value'])
            string.initializer = string_const
            string.global_constant = True
            string.linkage = LINKAGE_INTERNAL
            return string.gep((Constant.int(Type.int(), 0), Constant.int(Type.int(), 0)))
        elif expr['Type'] == 'UnaryOp':
            return self.gen_expr_unary(expr)
        elif expr['Type'] == 'BinaryOp':
            if expr['Op']['MetaType'] == 'ArithmOp':
                return self.gen_expr_arithm(expr)
            elif expr['Op']['MetaType'] == 'LogOp':
                return self.gen_expr_log(expr)
            else:
                return self.gen_expr_rel(expr)
        elif expr['Type'] == 'Var':
            return self.gen_expr_var(expr)
        elif expr['Type'] == 'FunCall':
            return self.gen_expr_funcall(expr)
        elif expr['Type'] in ('NewArrayPrimitive', 'NewArrayObject'):
            return self.gen_expr_new_arr(expr)
        elif expr['Type'] == 'NewObject':
            return self.gen_expr_new_object(expr)
        elif expr['Type'] == 'Attribute':
            return self.gen_expr_attribute(expr)
        elif expr['Type'] == 'ArrSubscript':
            return self.gen_expr_arr_subscript(expr)
        elif expr['Type'] == 'MethodCall':
            return self.gen_expr_method_call(expr)
        elif expr['Type'] == 'Cast':
            return self.gen_expr_cast(expr)
        elif expr['Type'] == 'Null':
            return self.gen_expr_null(expr)


    def set_blocks_to_none(self):
        self.__true_block = None
        self.__false_block = None


    def gen_if_stmt(self, stmt):
        function = self.__llvm_builder.basic_block.function
        self.__true_block = true_block = function.append_basic_block('then')
        if stmt['Type'] == 'IfElseStmt':
            self.__false_block = false_block = function.append_basic_block('else')
            self.gen_expr(stmt['Condition'])
            self.set_blocks_to_none()
            self.__llvm_builder.position_at_end(true_block)
            self.__push_env()
            self.gen_stmt(stmt['Stmt1'])
            self.__pop_env()
            if not stmt['Stmt1']['Returns']:
                end_block = function.append_basic_block('endif')
                self.__llvm_builder.branch(end_block)
            self.__llvm_builder.position_at_end(false_block)
            self.__push_env()
            self.gen_stmt(stmt['Stmt2'])
            self.__pop_env()
            if not stmt['Stmt2']['Returns']:
                self.__llvm_builder.branch(end_block)
                self.__llvm_builder.position_at_end(end_block)
        else:
            end_block = function.append_basic_block('endif')
            self.__false_block = end_block
            self.gen_expr(stmt['Condition'])
            self.set_blocks_to_none()
            self.__llvm_builder.position_at_end(true_block)
            self.__push_env()
            self.gen_stmt(stmt['Stmt'])
            self.__pop_env()
            if not stmt['Stmt']['Returns']:
                self.__llvm_builder.branch(end_block)
            self.__llvm_builder.position_at_end(end_block)
        self.__llvm_builder.add(Constant.int(Type.int(), 1), Constant.int(Type.int(), 1), 'nop')


    def __get_size_and_arr_ptr(self, struct_ptr):
        size_ptr = self.__llvm_builder.gep(struct_ptr,
            (Constant.int(Type.int(), 0), Constant.int(Type.int(), 0)))
        arr_ptr = self.__llvm_builder.gep(struct_ptr,
            (Constant.int(Type.int(), 0), Constant.int(Type.int(), 1)))
        return size_ptr, arr_ptr


    def gen_stmt_var_decl(self, stmt):
        alloca_type = None
        type_name = stmt['LatteType']['TypeName']
        if stmt['LatteType']['MetaType'] == 'Array':
            for item in stmt['Items']:
                malloc_type = PRIMITIVE_TYPE_OBJS[type_name] if type_name in PRIMITIVES\
                        else Type.pointer(self.__class_structs[type_name])
                array_struct = None
                if item['Assigned']:
                    item['Assigned']['MallocType'] = malloc_type
                    array_struct = self.gen_expr(item['Assigned'])
                else:
                    array_struct = self.__llvm_builder.alloca(Type.struct((Type.int(), Type.pointer(malloc_type))))
                    size_ptr, array_ptr = self.__get_size_and_arr_ptr(array_struct)
                    self.__llvm_builder.store(Constant.int(Type.int(), 0), size_ptr)
                    self.__llvm_builder.store(ConstantPointerNull.null(Type.pointer(malloc_type)), array_ptr)
                self.__function_envs[-1][item['Name']] = array_struct
                self.__function_meta_envs[-1][item['Name']] = item
                self.__function_meta_envs[-1][item['Name']]['LatteType'] = stmt['LatteType']
        elif stmt['LatteType']['TypeName'] == 'string':
            for item in stmt['Items']:
                if item['Assigned']:
                    var_val = self.gen_expr(item['Assigned'])
                else:
                    var_val = self.gen_zero(stmt)
                alloca = self.__llvm_builder.alloca(var_val.type, item['Name'])
                self.__llvm_builder.store(var_val, alloca)
                self.__function_envs[-1][item['Name']] = alloca
                self.__function_meta_envs[-1][item['Name']] = item
                self.__function_meta_envs[-1][item['Name']]['LatteType'] = stmt['LatteType']

        elif stmt['LatteType']['MetaType'] == 'Primitive':
            for item in stmt['Items']:
                alloca = self.__llvm_builder.alloca(PRIMITIVE_TYPE_OBJS[type_name], item['Name'])
                if item['Assigned']:
                    var_val = self.gen_expr(item['Assigned'])
                else:
                    var_val = self.gen_zero(stmt)

                self.__llvm_builder.store(var_val, alloca)
                self.__function_envs[-1][item['Name']] = alloca
                self.__function_meta_envs[-1][item['Name']] = item
                self.__function_meta_envs[-1][item['Name']]['LatteType'] = stmt['LatteType']
        elif stmt['LatteType']['MetaType'] == 'Class':
            for item in stmt['Items']:
                object_type = self.__class_structs[type_name]
                obj_ptr = self.__llvm_builder.alloca(Type.pointer(object_type), type_name + '_obj_pointer')
                if item['Assigned']:
                    item['Assigned']['ObjectName'] = item['Name']
                    var_ref = self.gen_expr(item['Assigned'])
                    self.__llvm_builder.store(var_ref, obj_ptr)
                else:
                    self.__llvm_builder.store(Constant.null(Type.pointer(object_type)), obj_ptr)
                self.__function_envs[-1][item['Name']] = obj_ptr
                self.__function_meta_envs[-1][item['Name']] = item
                self.__function_meta_envs[-1][item['Name']]['LatteType'] = stmt['LatteType']


    def gen_stmt_while_loop(self, stmt):
        function = self.__llvm_builder.basic_block.function
        cond_block = function.append_basic_block('while_cond')
        self.__llvm_builder.branch(cond_block)
        self.__true_block = loop_block = function.append_basic_block('loop')
        self.__false_block = merge_block = function.append_basic_block('endwhile')
        self.__llvm_builder.position_at_end(cond_block)
        condition = self.gen_expr(stmt['Condition'])
        self.set_blocks_to_none()
        self.__llvm_builder.position_at_end(loop_block)
        self.__push_env()
        self.gen_stmt(stmt['Stmt'])
        self.__pop_env()
        self.__llvm_builder.branch(cond_block)
        self.__llvm_builder.position_at_end(merge_block)


    def get_element(self, stmt, lvalue_latte, lvalue_ast):
        if stmt['LValue']['Type'] == 'LArrSubscript':
            index = self.gen_expr(stmt['LValue']['Subscript'])
            array_ptr = self.__llvm_builder.gep(lvalue_latte,
                (Constant.int(Type.int(), 0), Constant.int(Type.int(), 1)))
            array = self.__llvm_builder.load(array_ptr)
            lvalue_latte = self.__llvm_builder.gep(array, (index,))
        elif stmt['LValue']['Type'] == 'LAttribute':
            index = len(self.__class_meta[lvalue_ast['LatteType']['TypeName']].attributes_keys) - 1 -\
                (self.__class_meta[lvalue_ast['LatteType']['TypeName']].attributes_keys)[::-1].index(stmt['LValue']['Attr'])
            lvalue_ptr = self.__llvm_builder.load(lvalue_latte)
            lvalue_latte = self.__llvm_builder.gep(lvalue_ptr,
                    (Constant.int(Type.int(), 0), Constant.int(Type.int(), index),))
        return lvalue_latte


    def gen_stmt_assign(self, stmt):
        stmt['Expr']['ObjectName'] = stmt['LValue']['Name']
        value = self.gen_expr(stmt['Expr'])
        lvalue_ast = get_var(self.__function_meta_envs,
                stmt['LValue'], self.__class_meta, self.__current_class)
        lvalue_from_env = get_var(self.__function_envs,
                stmt['LValue'], self.__class_meta, self.__current_class)
        meta_type = lvalue_ast['LatteType']['MetaType']
        if stmt['LValue']['Type'] == 'LArrSubscript':
            meta_type = 'Primitive'
        lvalue_latte = self.get_element(stmt, lvalue_from_env, lvalue_ast)
        if meta_type in ('Primitive', 'Class'):
            self.__llvm_builder.store(value, lvalue_latte)
        elif meta_type == 'Array':
            size_ptr_l = self.__llvm_builder.gep(lvalue_latte,
                (Constant.int(Type.int(), 0), Constant.int(Type.int(), 0)))
            size_ptr_r = self.__llvm_builder.gep(value,
                (Constant.int(Type.int(), 0), Constant.int(Type.int(), 0)))
            array_ptr_l = self.__llvm_builder.gep(lvalue_latte,
                (Constant.int(Type.int(), 0), Constant.int(Type.int(), 1)))
            array_ptr_r = self.__llvm_builder.gep(value,
                (Constant.int(Type.int(), 0), Constant.int(Type.int(), 1)))
            size = self.__llvm_builder.load(size_ptr_r)
            self.__llvm_builder.store(size, size_ptr_l)
            array_ptr = self.__llvm_builder.load(array_ptr_r)
            self.__llvm_builder.store(array_ptr, array_ptr_l)


    def gen_stmt_ret(self, stmt):
        self.__current_function_returns = True
        if stmt['Expr']:
            self.__llvm_builder.ret(self.gen_expr(stmt['Expr']))
        else:
            self.__llvm_builder.ret_void()


    def gen_stmt_inc_dec(self, stmt):
        lvalue_latte = get_var(self.__function_envs, stmt['LValue'],
                self.__class_meta, self.__current_class)
        lvalue_ast = get_var(self.__function_meta_envs,
                stmt['LValue'], self.__class_meta, self.__current_class)
        lvalue_latte = self.get_element(stmt, lvalue_latte, lvalue_ast)
        lvalue = self.__llvm_builder.load(lvalue_latte)
        if stmt['Op'] == '++':
            result = self.__llvm_builder.add(lvalue, Constant.int(Type.int(), 1))
        else:
            result = self.__llvm_builder.sub(lvalue, Constant.int(Type.int(), 1))
        self.__llvm_builder.store(result, lvalue_latte)


    def gen_stmt_block(self, stmt):
        self.__push_env()
        for internal_stmt in stmt['Stmts']:
            self.gen_stmt(internal_stmt)
        self.__pop_env()


    def gen_stmt_for(self, stmt):
        self.__push_env()
        self.gen_stmt_var_decl(stmt['LoopVar'])
        array_struct_ptr = get_var(self.__function_envs, stmt, self.__class_meta, self.__current_class)
        size_ptr, array_ptr = self.__get_size_and_arr_ptr(array_struct_ptr)
        index_alloca = self.__llvm_builder.alloca(Type.int())
        self.__llvm_builder.store(Constant.int(Type.int(), 0), index_alloca)
        function = self.__llvm_builder.basic_block.function

        cond_block = function.append_basic_block('for_cond')
        loop_block = function.append_basic_block('for_loop')
        merge_block = function.append_basic_block('endfor')
        self.__llvm_builder.branch(cond_block)
        self.__llvm_builder.position_at_end(cond_block)
        size = self.__llvm_builder.load(size_ptr)
        current_loop_var_val = self.__llvm_builder.load(index_alloca)
        cond = self.__llvm_builder.icmp(ICMP_SLT, current_loop_var_val, size)
        self.__llvm_builder.cbranch(cond, loop_block, merge_block)

        self.__llvm_builder.position_at_end(loop_block)
        array = self.__llvm_builder.load(array_ptr)
        elem_ptr = self.__llvm_builder.gep(array, (current_loop_var_val,))
        loop_var_ptr = get_var(self.__function_envs, stmt['LoopVar'], self.__class_meta, self.__current_class)
        elem = self.__llvm_builder.load(elem_ptr)
        self.__llvm_builder.store(elem, loop_var_ptr)
        self.__push_env()
        self.gen_stmt(stmt['Stmt'])
        self.__pop_env()
        new_index = self.__llvm_builder.add(self.__llvm_builder.load(index_alloca), Constant.int(Type.int(), 1))
        self.__llvm_builder.store(new_index, index_alloca)
        self.__llvm_builder.branch(cond_block)
        self.__llvm_builder.position_at_end(merge_block)


        self.__pop_env()


    def gen_stmt(self, stmt):
        if stmt['Type'] == 'VariableDecl':
            self.gen_stmt_var_decl(stmt)
        elif stmt['Type'] == 'WhileLoop':
            self.gen_stmt_while_loop(stmt)
        if stmt['Type'] in ('IfStmt', 'IfElseStmt'):
            self.gen_if_stmt(stmt)
        elif stmt['Type'] == 'Expr':
            self.gen_expr(stmt['Expr'])
        elif stmt['Type'] == 'IncDec':
            self.gen_stmt_inc_dec(stmt)
        elif stmt['Type'] == 'Assignment':
            self.gen_stmt_assign(stmt)
        elif stmt['Type'] == 'Return':
            self.gen_stmt_ret(stmt)
        elif stmt['Type'] == 'Block':
            self.gen_stmt_block(stmt)
        elif stmt['Type'] == 'ForLoop':
            self.gen_stmt_for(stmt)


    def gen_zero(self, object_):
        if object_['LatteType']['TypeName'] == 'int':
            return Constant.int(Type.int(), 0)
        elif object_['LatteType']['TypeName'] == 'boolean':
            return Constant.int(Type.int(1), 0)
        elif object_['LatteType']['TypeName'] == 'string':
            string_const = Constant.stringz("")
            string = self.__module.add_global_variable(string_const.type, 'NullString')
            string.initializer = string_const
            string.global_constant = True
            string.linkage = LINKAGE_INTERNAL
            return string.gep((Constant.int(Type.int(), 0), Constant.int(Type.int(), 0)))
        else:
            return Constant.null(Type.pointer(self.__class_structs[object_['LatteType']['TypeName']]))


    def gen_class_ctor(self, class_):
        def create_ctor_header(struct_type, name):
            ctor = Function.new(self.__module,
                    Type.function(Type.void(), (Type.pointer(struct_type),)), name)
            ctor.linkage = LINKAGE_LINKONCE_ODR
            ctor_block = ctor.append_basic_block('entry')
            ctor_builder = Builder.new(ctor_block)
            ctor.args[0].name = 'this'
            param_alloca = ctor_builder.alloca(Type.pointer(struct_type))
            ctor_builder.store(ctor.args[0], param_alloca)
            this = ctor_builder.load(param_alloca)
            return ctor, ctor_builder, this

        def create_ctor_rest(this, ctor_builder):
            if class_['Extends']:
                ctor_builder.call(
                    self.__module.get_function_named(
                        class_['Extends'] + '_._cast_ctor_' + class_['Name']), (this,))
            own_attr_index = self.__class_meta[class_['Name']].base_class_arguments_len
            for index, attribute in enumerate(self.__class_meta[class_['Name']].own_attribute_keys, own_attr_index):
                field_ptr = ctor_builder.gep(this,
                    (Constant.int(Type.int(), 0), Constant.int(Type.int(), index)))
                ctor_builder.store(self.gen_zero(self.__class_meta[class_['Name']].attributes[attribute]), field_ptr)
            ctor_builder.ret_void()

        struct_type = self.__class_structs[class_['Name']]
        default_ctor, default_ctor_builder, this = create_ctor_header(struct_type, class_['Name'] + DEFAULT_CTOR_MANGLING)
        create_ctor_rest(this, default_ctor_builder)
        derived = (derived_class for derived_class in self.__classes if derived_class['Extends'] == class_['Name'])
        for derived_class in derived:
            struct_type_derived = self.__class_structs[derived_class['Name']]
            cast_ctor, cast_ctor_builder, this_derived = create_ctor_header(struct_type_derived,
                    class_['Name'] + '_._cast_ctor_' + derived_class['Name'])
            this = cast_ctor_builder.bitcast(this_derived, Type.pointer(struct_type))
            create_ctor_rest(this, cast_ctor_builder)


    def get_function_type(self):
        arg_types = []
        for arg in self.current_function_ast['ListArg']:
            if arg['LatteType']['MetaType'] != 'Array':
                arg_types.append(self.get_type(arg))
            else:
                arg_types.append(Type.pointer(self.get_type(arg)))
        return_type = None
        if self.current_function_ast['LatteType']['MetaType'] != 'Array':
            return_type = self.get_type(self.current_function_ast)
        else:
            return_type = Type.pointer(self.get_type(self.current_function_ast))
        return Type.function(return_type, arg_types, False)


    def __push_env(self):
        self.__function_envs.append({})
        self.__function_meta_envs.append({})
        param_counter = 1


    def __pop_env(self):
        self.__function_envs.pop()
        self.__function_meta_envs.pop()


    def get_type(self, latte_object):
        if latte_object['LatteType']['MetaType'] == 'Array':
            type_ = None
            if latte_object['LatteType']['TypeName'] in PRIMITIVES and\
                latte_object['LatteType']['TypeName'] != 'string':
                type_ = PRIMITIVE_TYPE_OBJS[latte_object['LatteType']['TypeName']]
            elif latte_object['LatteType']['TypeName'] in self.__class_structs:
                type_ = self.__class_structs[latte_object['LatteType']['TypeName']]
            elif latte_object['LatteType']['TypeName'] == 'string':
                type_ = Type.pointer(Type.int(SIZEOF_BYTE))
            return Type.struct((Type.int(), Type.pointer(type_)))
        if latte_object['LatteType']['TypeName'] in PRIMITIVES and\
                latte_object['LatteType']['TypeName'] != 'string':
            return PRIMITIVE_TYPE_OBJS[latte_object['LatteType']['TypeName']]
        elif latte_object['LatteType']['TypeName'] == 'string':
            return Type.pointer(Type.int(SIZEOF_BYTE))
        elif latte_object['LatteType']['TypeName'] in self.__class_structs:
            return Type.pointer(self.__class_structs[latte_object['LatteType']['TypeName']])


    def gen_class_struct(self, class_):
        subclass_attributes_len = len(self.__class_meta[class_['Name']].attributes.keys())
        self.__class_meta[class_['Name']].own_attribute_keys = self.__class_meta[class_['Name']].attributes.keys()
        if class_['Extends']:
            self.__class_meta[class_['Name']].attributes_keys = self.__class_meta[class_['Extends']].attributes_keys
            self.__class_meta[class_['Name']].attributes_keys += self.__class_meta[class_['Name']].attributes.keys()
            self.__class_meta[class_['Name']].attributes.update(self.__class_meta[class_['Extends']].attributes)
        else:
            self.__class_meta[class_['Name']].attributes_keys = self.__class_meta[class_['Name']].attributes.keys()
        self.__class_meta[class_['Name']].base_class_arguments_len =\
                len(self.__class_meta[class_['Name']].attributes_keys) - subclass_attributes_len
        self.__class_structs[class_['Name']] = Type.opaque('class.' + class_['Name'])
        body = [self.get_type(self.__class_meta[class_['Name']].attributes[attr_name])
            for attr_name in self.__class_meta[class_['Name']].attributes_keys]
        self.__class_structs[class_['Name']].set_body(body)


    def generate_llvm(self):
        for class_ in self.__classes:
            self.gen_class_struct(class_)

        for class_ in self.__classes:
            self.gen_class_ctor(class_)

        for function_name, function in (x for x in self.__functions.iteritems() if x[0] not in BUILTINS_INFO):
            self.current_function_ast = function
            self.__llvm_functions[function_name] = Function.new(self.__module, self.get_function_type(), function_name)


        for function_name, function in (x for x in self.__functions.iteritems() if x[0] not in BUILTINS_INFO):
            self.__current_function_returns = False
            self.__push_env()
            self.current_function_llvm = self.__llvm_functions[function_name]
            self.__current_block = self.current_function_llvm.append_basic_block('entry')
            self.__llvm_builder = Builder.new(self.__current_block)
            for arg, arg_passed in zip(self.current_function_llvm.args, function['ListArg']):
                arg.name = arg_passed['Name']
                if arg_passed['LatteType']['MetaType'] in ('Primitive', 'Class'):
                    alloca = self.__llvm_builder.alloca(self.get_type(arg_passed), arg.name)
                    self.__llvm_builder.store(arg, alloca)
                    self.__function_envs[-1][arg_passed['Name']] = alloca
                elif arg_passed['LatteType']['MetaType'] == 'Array':
                    self.__function_envs[-1][arg_passed['Name']] = arg
                self.__function_meta_envs[-1][arg_passed['Name']] = arg_passed
            for stmt in function['Body']['Stmts']:
                self.gen_stmt(stmt)
            if not self.__current_function_returns and function['LatteType']['TypeName']:
                self.__llvm_builder.ret_void()
            self.current_function_llvm.verify()
            self.__pop_env()
        #print self.__module
