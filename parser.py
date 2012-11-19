import ply.yacc as yacc
import sys

from lexer import LatteLexer

class LatteParser:
    tokens = LatteLexer.tokens[1:]

    def p_empty(self, p):
        'empty :'
        pass

    def p_Program(self, p):
        'Program : ListTopDef'
        p[0] = p[1]

    def p_TopDef(self, p):
        'TopDef : Type ID PAR_L ListArg PAR_R Block'
        p[0] = {'Type': 'FunDecl', 'LineNo': p.lineno(1), 'Name': p[2],
                'ListArg': p[4], 'Body': p[6], 'LatteType': p[1],
                'StartPos': p[1]['StartPos'], 'EndPos': p[6]['EndPos']}

    def p_TopDef_error(self, p):
        'TopDef : ID PAR_L ListArg PAR_R Block'
        print >> sys.stderr, 'ERROR: undeclared return type: in declaration of %s, line: %d, pos: %d - %d' %\
                (p[1], p.lineno(1), p.lexpos(1), p[5]['EndPos'])

    def p_ListTopDef_empty(self, p):
        'ListTopDef : empty'
        p[0] = []

    def p_ListTopDef_list(self, p):
        'ListTopDef : ListTopDef TopDef'
        p[1].append(p[2])
        p[0] = p[1]

    def p_ListArg_empty(self, p):
        'ListArg : empty'
        p[0] = []

    def p_ListArg_single(self, p):
        'ListArg : Arg'
        p[0] = [p[1]]

    def p_ListArg_list(self, p):
        'ListArg : ListArg COMMA Arg'
        if p[1]:
            p[1].append(p[3])
            p[0] = p[1]
        else:
            p[0] = p[3]

    def p_Arg(self, p):
        'Arg : Type ID'
        p[0] = {'Name': p[2], 'LatteType': p[1], 'StartPos': p[1]['StartPos'], 'EndPos': p.lexpos(2)}


    def p_Type(self, p):
        '''Type : INT
                | BOOL
                | STRING
                | VOID'''
        p[0] = {'TypeName': p[1], 'LineNo': p.lineno(1), \
                'StartPos': p.lexpos(1), 'EndPos': p.lexpos(1) + len(p[1])}

    def p_Block(self, p):
        'Block : BR_L ListStmt BR_R'
        p[0] = {'Type': 'Block', 'LineNo': p.lineno(1), 'Stmts': p[2],
                'StartPos': p.lexpos(1), 'EndPos': p.lexpos(3)}

    def p_Stmt_vardecl(self, p):
        'Stmt : Type ListItem END_S'
        p[0] = {'Type': 'VariableDecl', 'LineNo': p.lineno(1), 'LatteType': p[1], 'Items': p[2],
                'StartPos': p[1]['StartPos'], 'EndPos': p.lexpos(3)}

    def p_ListStmt_empty(self, p):
        'ListStmt : empty'
        p[0] = []

    def p_ListStmt_list(self, p):
        'ListStmt : ListStmt Stmt'
        p[1].append(p[2])
        p[0] = p[1]

    def p_Stmt_while(self, p):
        'Stmt : WHILE PAR_L Expr PAR_R Stmt'
        p[0] = {'Type': 'WhileLoop', 'LineNo': p.lineno(1), 'Condition': p[3], 'Stmt': p[5],
                'StartPos': p.lexpos(1), 'EndPos': p[5]['EndPos']}

    def p_Stmt_while_error(self, p):
        'Stmt : WHILE PAR_L error PAR_R Stmt'
        print >> sys.stderr, 'Syntax error: invalid expression in while loop condition, line: %d, pos: %d' %\
                (p.lineno(3), p.lexpos(2) + 1)

    def p_Stmt_end(self, p):
        'Stmt : END_S'
        p[0] = {'Type': 'End', 'StartPos': p.lexspan(1), 'EndPos': p.lexspan(1)}

    def p_Stmt_if(self, p):
        'Stmt : IF PAR_L Expr PAR_R Stmt'
        p[0] = {'Type': 'IfStmt', 'LineNo': p.lineno(1), 'Condition': p[3], 'Stmt': p[5],
                'StartPos': p.lexpos(1), 'EndPos': p[5]['EndPos']}

    def p_Stmt_if_error(self, p):
        'Stmt : IF PAR_L error PAR_R Stmt'
        print >> sys.stderr, 'Syntax error: invalid expression in if statement condition, line %d, pos %d' %\
                (p.lineno(3), p.lexpos(2) + 1)

    def p_Stmt_ifelse(self, p):
        'Stmt : IF PAR_L Expr PAR_R Stmt ELSE Stmt'
        p[0] = {'Type': 'IfElseStmt', 'LineNo': p.lineno(1), 'Condition': p[3],
                'Stmt1': p[5], 'Stmt2': p[7], 'StartPos': p.lexpos(1), 'EndPos': p[5]['EndPos']}

    def p_Stmt_ifelse_error(self, p):
        'Stmt : IF PAR_L error PAR_R Stmt ELSE Stmt'
        print >> sys.stderr, 'Syntax error: invalid expression in if/else statement condition, line %d, pos %d' %\
                (p.lineno(3), p.lexpos(2) + 1)

    def p_Stmt_expr(self, p):
        'Stmt : Expr END_S'
        p[0] = {'Type': 'Expr', 'LineNo': p.lineno(1), 'Expr': p[1],
                'StartPos': p[1]['StartPos'], 'EndPos': p.lexpos(2)}

    def p_Stmt_block(self, p):
        'Stmt : Block'
        p[0] = p[1]

    def p_Stmt_assign(self, p):
        'Stmt : ID ASSIGN Expr END_S'
        p[0] = {'Type': 'Assignment', 'LineNo': p.lineno(1), 'Name': p[1], 'Expr': p[3],
                'StartPos': p.lexpos(1), 'EndPos': p.lexpos(4)}

    def p_Stmt_inc_dec(self, p):
        '''Stmt : ID INC END_S
              | ID DEC END_S'''
        p[0] = {'Type': 'IncDec', 'LineNo': p.lineno(1), 'Name': p[1], 'Op': p[2],
                'StartPos': p.lexpos(1), 'EndPos': p.lexpos(3)}

    def p_Stmt_ret(self, p):
        'Stmt : RET Expr END_S'
        p[0] = {'Type': 'Return', 'LineNo': p.lineno(1), 'Expr': p[2],
                'StartPos': p.lexpos(1), 'EndPos': p.lexpos(2)}

    def p_Stmt_ret_noexp(self, p):
        'Stmt : RET END_S'
        p[0] = {'Type': 'Return', 'LineNo': p.lineno(1), 'Expr': None,
                'StartPos': p.lexpos(1), 'EndPos': p.lexpos(2)}

    def p_Item_noinit(self, p):
        'Item : ID'
        p[0] = {'Name': p[1], 'Assigned': None, 'LineNo': p.lineno(1),
                'StartPos': p.lexpos(1), 'EndPos': p.lexpos(1) + len(p[1])}

    def p_Item_init(self, p):
        'Item : ID ASSIGN Expr'
        p[0] = {'Name': p[1], 'Assigned': p[3], 'LineNo': p.lineno(1),
                'StartPos': p.lexpos(1), 'EndPos': p[3]['EndPos']}


    def p_ListItem_empty(self, p):
        'ListItem : Item'
        p[0] = [p[1]]

    def p_ListItem_list(self, p):
        'ListItem : ListItem COMMA Item'
        p[1].append(p[3])
        p[0] = p[1]

    def p_AddOp(self, p):
        '''AddOp : PLUS
               | MINUS'''
        p[0] = {'Op': p[1], 'StartPos': p.lexpos(1), 'EndPos': p.lexpos(1), 'MetaType': 'ArithmOp'}

    def p_MulOp(self, p):
        '''MulOp : TIMES
                 | MOD
                 | DIV'''
        p[0] = {'Op': p[1], 'StartPos': p.lexpos(1), 'EndPos': p.lexpos(1), 'MetaType': 'ArithmOp'}

    def p_RelOp(self, p):
        '''RelOp : LESS
                 | GT
                 | LEQ
                 | GEQ
                 | EQ
                 | NEQ'''
        p[0] = {'Op': p[1], 'StartPos': p.lexpos(1), 'EndPos': p.lexpos(1), 'MetaType': 'RelOp'}

    def p_Unary(self, p):
        '''UnaryOp : NOT
                   | MINUS'''
        p[0] = {'Op': p[1], 'StartPos': p.lexpos(1), 'EndPos': p.lexpos(1)}


    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('nonassoc', 'RelOp', 'LESS', 'GT', 'LEQ', 'GEQ', 'EQ', 'NEQ'),
        ('left', 'AddOp', 'PLUS', 'MINUS'),
        ('left', 'MulOp', 'TIMES', 'DIV', 'MOD'),
        ('right', 'UnaryOp')
    )

    def p_Expr_id(self, p):
        'Expr : ID'
        p[0] = {'Type':'Var', 'Name':p[1], 'LineNo':p.lineno(1),
                'StartPos':p.lexspan(1)[0], 'EndPos':(p.lexspan(1)[1] + len(p[1]))}

    def p_Expr_bool_literal(self, p):
        '''Expr : TRUE
                | FALSE'''
        p[0] = {'Type': 'BoolLiteral', 'Value': p[1], 'LineNo': p.lineno(1),
            'StartPos': p.lexspan(1)[0], 'EndPos': p.lexspan(1)[1] + len(str(p[1]))}
    def p_Expr_num_literal(self, p):
       'Expr : NUM'
       p[0] = {'Type': 'NumLiteral', 'Value': p[1], 'LineNo': p.lineno(1),
            'StartPos': p.lexspan(1)[0], 'EndPos': p.lexspan(1)[1] + len(str(p[1]))}

    def p_Expr_str_literal(self, p):
       'Expr : LITSTR'
       p[0] = {'Type': 'StrLiteral', 'Value': p[1], 'LineNo': p.lineno(1),
            'StartPos': p.lexspan(1)[0], 'EndPos': p.lexspan(1)[1] + len(str(p[1]))}

    def p_Expr_paren(self, p):
        'Expr : PAR_L Expr PAR_R'
        p[0] = p[2]

    def p_Expr_funcall(self, p):
        '''Expr : ID PAR_L ListExpr PAR_R'''
        p[0] = {'Type': 'FunCall', 'Name': p[1], 'ListArg': p[3], 'LineNo': p.lineno(1),
                'StartPos': p.lexpos(1), 'EndPos': p.lexpos(4)}

    def p_Expr_unary(self, p):
        'Expr : UnaryOp Expr %prec UnaryOp'
        p[0] = {'Type': 'UnaryOp', 'Op': p[1], 'Arg': p[2], 'LineNo': p.lineno(1),
                'StartPos': p[1]['StartPos'] - 1, 'EndPos': p[2]['EndPos']}

    def p_Expr_binop(self, p):
        '''Expr : Expr OR Expr
              | Expr AND Expr
              | Expr RelOp Expr %prec RelOp
              | Expr AddOp Expr %prec AddOp
              | Expr MulOp Expr %prec MulOp'''
        p[0] = {'Type': 'BinaryOp', 'Left': p[1], 'Op': p[2], 'Right': p[3],
                'LineNo': p.lineno(1), 'StartPos': p[1]['StartPos'], 'EndPos': p[3]['EndPos']}

    def p_ListExpr_empty(self, p):
        'ListExpr : empty'
        p[0]= []

    def p_ListExpr_Expr(self, p):
        'ListExpr : Expr'
        p[0] = [p[1]]

    def p_ListExpr_list(self, p):
        'ListExpr : ListExpr COMMA Expr'
        p[1].append(p[3])
        p[0] = p[1]

    def __init__(self):
        self.lexer = LatteLexer().build()
        self.parser = yacc.yacc(module=self, debug=True, start='Program')

    def parse(self, source):
        return yacc.parse(source, tracking=True, debug=0, lexer=self.lexer)

if __name__ == "__main__":
    p = LatteParser()
    fd = open(sys.argv[1])
    print p.parse(fd.read())

