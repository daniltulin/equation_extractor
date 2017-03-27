from enum import Enum

class Variable():
    def __init__(self, name):
        self.name = name
        self.dep = None

    def __repr__(self):
        return "Var: '" + self.name + "'"

    def __eq__(self, rhs):
        return self.name == rhs.name

    def equation(self):
        return self.dep.equation_for(self.name)

    @staticmethod
    def Factory(tokens):
        return Variable(tokens[0])

class InputVariable(Variable):
    def __repr__(self):
        return 'Input' + Variable.__repr__(self)

    def equation(self):
        return Equation(self)

    @staticmethod
    def Factory(tokens):
        return InputVariable(tokens[0])

class ConstantVariable(Variable):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def equation(self):
        return Equation(self)

    def __repr__(self):
        return "Const" + Variable.__repr__(self) + ", " + repr(self.value)

class Policy(Enum):
    OR = 0
    AND = 1

class Equation:
    def __init__(self, variable=None):
        self.inputs = None
        self.variable = variable
        if not variable is None:
            self.inputs = {variable.name}

        self.components = None
        self.policy =  None
        self.representation = None

    def append(self, rhs, bit, policy):
        pair = (bit, rhs)
        components = self.components
        if components is None:
            self.policy = policy
            self.components = [pair]
            self.inputs = rhs.inputs
            return
        assert self.policy == policy
        components.append(pair)
        self.inputs |= rhs.inputs

    def OR(self, *args):
        self.append(*args, Policy.OR)

    def AND(self, *args):
        self.append(*args, Policy.AND)

    def __repr__(self):
        if not self.representation is None:
            return self.representation
        variable = self.variable
        if not variable is None:
            return variable.name
        joiner = ' || ' if self.policy == Policy.OR else ' && '
        def build(b, e):
            neg = '!' if b else ''
            return neg + repr(e)
        components = [build(b, e) for b, e in self.components]
        def wrap(x):
            if len(components) > 1:
                return '(' + x + ')'
            return x
        self.representation = wrap(joiner.join(components))
        return self.representation

    def substitute(self, mapping):
        if self.policy is None:
            name = self.variable.name
            if name in mapping:
                return mapping[self.variable.name].equation()
        else:
            self.inputs = set()
            for i, pair in enumerate(self.components):
                bit, component = pair
                equation = component.substitute(mapping)
                self.components[i] = (bit, equation)
                self.inputs |= equation.inputs
        return self

    def evaluate(self, mapping):
        variable = self.variable
        if not variable is None:
            if isinstance(variable, ConstantVariable):
                return variable.value
            return mapping[variable.name]
        for bit, equation in self.components:
            if self.policy == Policy.AND:
                if bit != equation.evaluate(mapping):
                    return False
            elif bit == equation.evaluate(mapping):
                return True
        return True
