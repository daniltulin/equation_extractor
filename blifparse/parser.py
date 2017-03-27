from pyparsing import Word, OneOrMore, Suppress, alphanums, alphas
from pyparsing import StringEnd, Optional, ParserElement, Group

class Bit():
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        try:
            return str(int(self.value))
        except:
            return '-'

    @staticmethod
    def Factory(tokens):
        try:
            return Bit(bool(int(tokens[0])))
        except:
            return Bit(None)

class Bits():
    def __init__(self, bits):
        self.bits = bits

    def __repr__(self):
        return ''.join([repr(bit) for bit in self.bits])

    @staticmethod
    def Factory(tokens):
        return Bits([Bit.Factory([t]) for t in tokens[0]])

class Variable():
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Var: '" + self.name + "'"

    @staticmethod
    def Factory(tokens):
        return Variable(tokens[0])

class InputVariable(Variable):
    def __repr__(self):
        return 'Input' + Variable.__repr__(self)

class ConstantVariable(Variable):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return "Const" + Variable.__repr__(self) + ", " + repr(self.value)

class LogicGate():
    def __init__(self, inputs, output, masks, output_mask):
        self.inputs = inputs
        self.output = output
        self.masks = masks
        self.output_mask = output_mask

    def __repr__(self):
        return 'Logic gate: inputs: ' + repr(self.inputs) + ', output: ' +\
                repr(self.output) + ', masks: ' + repr(self.masks) +\
                ', output_mask: ' + repr(self.output_mask)

    @staticmethod
    def Factory(result):
        variables = result.variables
        inputs = variables[:-1]
        output = variables[-1]

        covers = result.covers

        if len(inputs) == 0:
            bit = covers[0].output_bit
            if bit.value is None:
                return InputVariable(output.name)
            else:
                return ConstantVariable(output.name, bit)

        masks = [cover.mask for cover in covers]
        output_mask = Bits([cover.output_bit for cover in covers])
        return LogicGate(inputs, output, masks, output_mask)

class LibraryGate():
    def __init__(self, model_name, assignments):
        self.model_name = model_name
        self.assignments = assignments

    def __repr__(self):
        return 'Library gate: ' + self.model_name + ', ' +\
                ', '.join([a.name + '=' + b.name
                           for a, b in self.assignments.items()])

    @staticmethod
    def Factory(result):
        model_name = result.model_name
        assignments = {assignment.actual: assignment.formal
                       for assignment in result.assignments}
        return LibraryGate(model_name, assignments)

class Latch():
    @staticmethod
    def Factory(result):
        return InputVariable(result.output)

class Model():
    def __init__(self, name, inputs, constants, outputs, commands):
        self.name = name
        self.inputs = inputs
        self.constants = constants
        self.outputs = outputs
        self.commands = commands

    def __repr__(self):
        return 'Model: ' + self.name + ' ' +\
                ', '.join(map(repr, [self.inputs, self.constants,
                                    self.outputs, self.commands]))

    @staticmethod
    def Factory(result):
        vectorize = lambda seq: [x for x in seq]
        name = result.name
        inputs = vectorize(result.inputs)
        outputs = vectorize(result.outputs)

        components = result.components
        filter_components = lambda f: [c for c in components if f(c)]

        commands = filter_components(lambda c: isinstance(c, LibraryGate) or\
                                               isinstance(c, LogicGate))
        constants = filter_components(lambda c: isinstance(c, ConstantVariable))
        input_variables = \
                filter_components(lambda c: isinstance(c, InputVariable))

        return Model(name, inputs + input_variables,
                     constants, outputs, commands)


class Parser():
    def parse(self, f):
        is_valuable_line = lambda l: len(l) > 0 and l[0] != '#'
        filtered_lines = [l for l in f if is_valuable_line(l)]
        text = ' '.join(filtered_lines).replace('\\', ' ')

        identifier = Word(alphas + '_', alphanums + '_')
        plain_name = Word(alphas + '_', alphanums + '_')

        model_name = Suppress('.model') + plain_name('name')

        identifier.setParseAction(Variable.Factory)
        identifier_list = OneOrMore(identifier)

        input_list = Suppress('.inputs') + Group(identifier_list)('inputs')
        output_list = Suppress('.outputs') + Group(identifier_list)('outputs')

        model_declaration = model_name + input_list + output_list

        variable_list = (identifier + Optional(identifier_list))

        bit = Word('01-', max=1)('output_bit')
        mask = Word('01-')('mask')

        bit.setParseAction(Bit.Factory)
        mask.setParseAction(Bits.Factory)

        output_cover = Group(bit | (mask + bit))
        output_covers = OneOrMore(output_cover)

        logic_gate = Suppress('.names') + Group(variable_list)('variables') +\
                     Group(output_covers)('covers')
        logic_gate.setParseAction(LogicGate.Factory)

        identifier_idc = Suppress(identifier)
        latch_variable_list = identifier_idc + plain_name('output')
        type_control_state = Suppress('re') + identifier_idc + Suppress('2')
        latch = Suppress('.latch') + latch_variable_list + type_control_state
        latch.setParseAction(Latch.Factory)

        formal_actual = Group(identifier('formal') + Suppress('=') +
                              identifier('actual'))
        assignments = Group(OneOrMore(formal_actual))
        library_gate = Suppress('.gate') + plain_name('model_name') +\
                       assignments('assignments')
        library_gate.setParseAction(LibraryGate.Factory)

        component = logic_gate | library_gate | latch

        end = Suppress('.end')
        model = model_declaration + OneOrMore(component)('components') + end
        model.setParseAction(Model.Factory)

        stringEnd = StringEnd()
        blif = OneOrMore(Group(model)) + stringEnd

        result = blif.parseString(text)
        return result
