from .equation import Equation

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
