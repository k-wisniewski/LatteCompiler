from maybe import Maybe

class LatteOptimizer:

    def __eval_expression_unary(self, expression, parent, key):
        if expression['Op']['Op'] == '-':
            result = -(self.__eval_expression(expression['Arg'], expression, 'Arg'))
            if result:
                parent[key] = {'Type': 'NumLiteral', 'Value': result.value,
                    'LineNo': expression['LineNo'], 'StartPos': expression['StartPos'], 'EndPos': expression['EndPos']}
            return result
        elif expression['Op']['Op'] == '!':
            result = not (self.__eval_expression(expression['Arg'], expression, 'Arg'))
            if result:
                parent[key] = {'Type': 'BoolLiteral', 'Value': result.value,
                    'LineNo': expression['LineNo'], 'StartPos': expression['StartPos'], 'EndPos': expression['EndPos']}
            return result

    def __rotate_expression_tree(parent, key):
        expression = parent['key']
        if expression['left']['Type'] == 'BinOp' and\
                expression['left']['Op'] == expression['Op']:


    def __eval_expression_binary(self, expression, parent, key):
        result = Maybe(None)
        if expression['Op'] == '&&':
            result = self.__eval_expression(expression['Left'], expression, 'Left') and\
                    self.__eval_expression(expression['Right'], expression, 'Right')
        elif expression['Op'] == '||':
            result = self.__eval_expression(expression['Left'], expression, 'Left') or\
                    self.__eval_expression(expression['Right'], expression, 'Right')
        elif expression['Op']['Op'] == '+':
            result = self.__eval_expression(expression['Left'], expression, 'Left') +\
                    self.__eval_expression(expression['Right'], expression, 'Right')
        elif expression['Op']['Op'] == '-':
            result = self.__eval_expression(expression['Left'], expression, 'Left') -\
            self.__eval_expression(expression['Right'], expression, 'Right')
        elif expression['Op']['Op'] == '*':
            result = self.__eval_expression(expression['Left'], expression, 'Left') *\
                    self.__eval_expression(expression['Right'], expression, 'Right')
        elif expression['Op']['Op'] == '/':
            result = self.__eval_expression(expression['Left'], expression, 'Left') //\
                    self.__eval_expression(expression['Right'], expression, 'Right')
        elif expression['Op']['Op'] == '%':
            result = self.__eval_expression(expression['Left'], expression, 'Left') %\
                    self.__eval_expression(expression['Right'], expression, 'Right')
        elif expression['Op']['Op'] == '<':
            result = self.__eval_expression(expression['Left'], expression, 'Left') <\
                    self.__eval_expression(expression['Right'], expression, 'Right')
        elif expression['Op']['Op'] == '<=':
            result = self.__eval_expression(expression['Left'], expression, 'Left') <=\
                    self.__eval_expression(expression['Right'], expression, 'Right')
        elif expression['Op']['Op'] == '>':
            result = self.__eval_expression(expression['Left'], expression, 'Left') >\
                    self.__eval_expression(expression['Right'], expression, 'Right')
        elif expression['Op']['Op'] == '>=':
            result = self.__eval_expression(expression['Left'], expression, 'Left') >=\
                    self.__eval_expression(expression['Right'], expression, 'Right')
        elif expression['Op']['Op'] == '==':
            result = self.__eval_expression(expression['Left'], expression, 'Left') ==\
                    self.__eval_expression(expression['Right'], expression, 'Right')
        elif expression['Op']['Op'] == '!=':
            result = self.__eval_expression(expression['Left'], expression, 'Left') !=\
                    self.__eval_expression(expression['Right'], expression, 'Right')

        if result == Maybe(None):
            self.__rotate_expression_tree(parent, key)
            result = self.__eval_expression(expression['Left'], expression, 'Left') and\
                self.__eval_expression(expression['Right'], expression, 'Right')


        if result.value != None:
            if expression['Op'] in ['&&', '||']:
                parent[key] = {'Type': 'BoolLiteral', 'Value': result.value,
                    'LineNo': expression['LineNo'], 'StartPos': expression['StartPos'], 'EndPos': expression['EndPos']}
            elif expression['Op']['Op'] in ['+', '-', '*', '/', '%']:
                parent[key] = {'Type': 'NumLiteral', 'Value': result.value,
                    'LineNo': expression['LineNo'], 'StartPos': expression['StartPos'], 'EndPos': expression['EndPos']}
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


    def simplify_expression(self, expression):
        d = {'result': expression}
        self.__eval_expression(expression, d, 'result')
        return d['result']

