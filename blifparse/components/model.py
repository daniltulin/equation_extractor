from .logicgate import LogicGate
from .librarygate import LibraryGate
from .equation import Variable, InputVariable, ConstantVariable

class Model():
    def __init__(self, name, inputs, input_variables, constants,
                 outputs, libraries, logics):
        self.name = name

        dictionarize = lambda seq: {x.name: x for x in seq}
        self.inputs = dictionarize(inputs)
        self.input_variables = dictionarize(input_variables)
        self.constants = dictionarize(constants)
        self.outputs = dictionarize(outputs)

        self.libraries = libraries
        self.logics = logics

        self.dependencies = None

    def link_with(self, models):
        for library in self.libraries:
            library.link_with(models)
            self.input_variables = {**self.input_variables,
                                    **library.model.input_variables}

        deps = {}
        for gate in (self.libraries + self.logics):
            for output in gate.outputs:
                deps[output] = gate
            for i, input_var in enumerate(gate.inputs):
                name = input_var.name
                if name in self.inputs:
                    gate.inputs[i] = self.inputs[name]
                elif name in self.constants:
                    gate.inputs[i] = self.constants[name]
                else:
                    prefixied = self.name + '.' + name
                    if prefixied in self.input_variables:
                        gate.inputs[i] = self.input_variables[prefixied]
        self.deps = deps

        for output in self.outputs.values():
            self.build_deps(output)

    def build_deps(self, variable):
        if isinstance(variable, ConstantVariable)\
           or isinstance(variable, InputVariable)\
           or not variable.dep is None:
            return
        gate = self.deps[variable.name]
        variable.dep = gate
        for input_var in gate.inputs:
            self.build_deps(input_var)

    def equation(self):
        return {var.name: var.equation() for var in self.outputs.values()}

    def __repr__(self):
        properties = [self.inputs.values(), self.input_variables.values(),
                      self.constants.values(), self.outputs.values(),
                      self.libraries, self.logics]
        return 'Model: ' + self.name + ' ' +\
                ', '.join(map(lambda x: str(list(x)), properties))

    @staticmethod
    def Factory(result):
        name = result.name
        vectorize = lambda seq: [x for x in seq]
        inputs = vectorize(result.inputs)
        outputs = vectorize(result.outputs)

        components = result.components
        filter_components = lambda f: [c for c in components if f(c)]

        libraries = filter_components(lambda c: isinstance(c, LibraryGate))
        logics = filter_components(lambda c: isinstance(c, LogicGate))
        constants = filter_components(lambda c: isinstance(c, ConstantVariable))

        def prefixied(x):
            x.name = name + '.' + x.name
            return x
        input_variables = [prefixied(var) for var in\
            filter_components(lambda c: isinstance(c, InputVariable))]

        return Model(name, inputs, input_variables, constants,
                     outputs, libraries, logics)
