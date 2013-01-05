class VariableUndeclared(Exception):
    def __init__(self, msg):
        self.msg = msg


def get_var(environments, node):
    for env in reversed(environments):
        if node['Name'] in env.keys():
            return env[node['Name']]
    raise VariableUndeclared('Variable %s is undeclared, line: %d, pos: %d - %d' %
            (node['Name'], node['LineNo'], node['StartPos'], node['EndPos']))


