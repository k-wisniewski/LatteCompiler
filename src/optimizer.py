import operator
from shared.maybe import Maybe

class LatteOptimizer:

    binOps = {
            '&&': operator.and_,
            '||': operator.or_,
            '+' : operator.add,
            '-' : operator.sub,
            '*' : operator.mul,
            '/' : operator.floordiv,
            '%' : operator.mod,
            '<' : operator.lt,
            '<=': operator.le,
            '>' : operator.gt,
            '>=': operator.ge,
            '==': operator.eq,
            '!=': operator.ne
            }

    def __eval_expression_unary(self, expression, parent, key):
        if expression['Op']['Op'] == '-':
            result = -(self.__eval_expression(expression['Arg'], expression, 'Arg'))
            if result:
                parent[key] = {'Type': 'NumLiteral', 'Value': result.value,
                    'LineNo': expression['LineNo'], 'StartPos': expression['StartPos'], 'EndPos': expression['EndPos']}
            return result
        elif expression['Op']['Op'] == '!':
            result = self.__eval_expression(expression['Arg'], expression, 'Arg')
            if result:
                result = not result
                parent[key] = {'Type': 'BoolLiteral', 'Value': result.value,
                    'LineNo': expression['LineNo'], 'StartPos': expression['StartPos'], 'EndPos': expression['EndPos']}
            return result


    def rotate_expression_tree(self, parent, key):
        expression = parent[key]
        literal_node = None
        non_literal_node = None
        expression_left = expression['Left']
        if not expression['Right']['Type'].endswith('Literal'):
            return
        if expression['Left']['Type'] == 'BinaryOp' and\
            expression['Left']['Op']['Op'] == expression['Op']['Op']:
            if expression['Left']['Left']['Type'].endswith('Literal'):
                literal_node = 'Left'
                non_literal_node = 'Right'
            elif expression['Left']['Right']['Type'].endswith('Literal'):
                literal_node = 'Right'
                non_literal_node = 'Left'
            if not literal_node:
                return
            expression['Left'] = expression['Left'][literal_node]
            expression_left['Left'] = expression_left[non_literal_node]
            expression_left['Right'] = expression
            parent[key] = expression_left


    def __eval_expression_binary(self, expression, parent, key):
        result = self.binOps[expression['Op']['Op']](self.__eval_expression(expression['Left'], expression, 'Left'),
                self.__eval_expression(expression['Right'], expression, 'Right'))

        if not result:
            self.rotate_expression_tree(parent, key)
            expression = parent[key]
            result = self.binOps[expression['Op']['Op']](self.__eval_expression(expression['Left'], expression, 'Left'),
                self.__eval_expression(expression['Right'], expression, 'Right'))

        if result.value != None:
            if expression['Op']['MetaType'] == 'ArithmOp':
                print expression['Left']
                parent[key] = {'Type': 'NumLiteral' if expression['Left']['EvalType'] != 'string' else 'StrLiteral',
                    'Value': result.value, 'LineNo': expression['LineNo'],
                    'StartPos': expression['StartPos'], 'EndPos': expression['EndPos']}
            else:
                parent[key] = {'Type': 'BoolLiteral', 'Value': result.value,
                    'LineNo': expression['LineNo'], 'StartPos': expression['StartPos'], 'EndPos': expression['EndPos']}
        return result


    def __eval_expression(self, expression, parent, key):
        if expression['Type'] in ['NumLiteral', 'BoolLiteral', 'StrLiteral']:
            return Maybe(expression['Value'])
        elif expression['Type'] == 'UnaryOp':
            return self.__eval_expression_unary(expression, parent, key)
        elif expression['Type'] == 'BinaryOp':
            return self.__eval_expression_binary(expression, parent, key)
        elif expression['Type'] in ['Var', 'FunCall']:
            return Maybe(None)


    def simplify_expression(self, dest_dict, key):
        expression = dest_dict[key]
        self.__eval_expression(expression, dest_dict, key)

