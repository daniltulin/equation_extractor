from re import compile, fullmatch

def without_emptys(seq):
    return [s for s in seq if len(s) > 0]

def wrap(seq, text):
    if len(seq) > 1:
        return '(' + text + ')'
    return text

class Node:
    def __init__(self, name, dep=None):
        self.name = name
        self.dep = dep
        self.expr = None

    def is_leaf(self):
        return self.dep is None

    def cache(self):
        if self.expr is None:
            self.expr = str(self.dep)
        return self.expr

    def __str__(self):
        if self.is_leaf():
            return self.name
        else:
            return self.cache()

class LogicGate:
    def __init__(self):
        self.input_nodes = None
        self.output_name = None

        self.input_masks = None
        self.output_mask = None

    def parse(self, text):
        # Split logic gate body
        lines = text.split('\n')
        variables = lines[0].split()
        logics = without_emptys(lines[1:])
        input_names = variables[:-1]
        output_name = variables[-1]

        # Parse logic board
        input_masks = []
        output_mask = []

        for logic in logics:
            input_bits, output_bit = logic.split()
            input_masks.append(input_bits)
            output_mask.append(output_bit)

        # Assign class fields
        self.input_nodes = [Node(name) for name in input_names]
        self.output_name = output_name

        self.input_masks = input_masks
        self.output_mask = output_mask

        return self

    def or_component(self, mask):
        nodes = self.input_nodes
        include = lambda b: b != '-'
        components_for_building = [(b, n) for b, n in zip(mask, nodes)
                                   if include(b)]
        def build(bit, node):
            neg = '!' if bit == '0' else ''
            return neg + str(node)

        components = [build(b, n) for b, n in components_for_building]
        result = '{}'.format(' and '.join(components))
        return wrap(components, result)

    def __str__(self):
        masks = self.input_masks
        components = [self.or_component(mask) for mask in masks]
        result = ' or '.join(components)
        return wrap(components, result)

class Model:
    def __init__(self):
        self.inputs = None
        self.outputs = None
        self.logic_gates = None

    def parse(self, text):
        lines = text.split('\n')

        # Take components of blif file
        model_name, input_token, output_token = lines[0:3]
        content = '\n'.join(lines[3:-1])
        end = lines[-1]

        # Inputs and outputs section
        _, input_names = input_token.split('.inputs')
        _, output_names = output_token.split('.outputs')

        self.inputs = {name: Node(name) for name in input_names.split()}
        self.outputs = {name: Node(name) for name in output_names.split()}

        # Content section
        text_logic_gates = without_emptys(content.split('.names '))
        logic_gates = [LogicGate().parse(t) for t in text_logic_gates]

        self.logic_gates = {gate.output_name: gate for gate in logic_gates}

        for output in self.outputs.values():
            self.build_dependencies(output)
        return self

    def build_dependencies(self, node):
        if node.name in self.inputs:
            return
        gate = self.logic_gates[node.name]
        node.dep = gate
        for input_node in gate.input_nodes:
            self.build_dependencies(input_node)

class Extractor:
    def __init__(self):
        self.model = None

    def parse(self, raw_text):
        # Filter lines
        is_valid = lambda l: len(l) > 0 and l[0] != '#'
        lines_without_comments = [line for line in raw_text.split('\n')
                                  if is_valid(line)]
        filtered_text = '\n'.join(lines_without_comments)

        # Header
        declaration = r'\.model \w+'
        inputs = r'\.inputs \w+( \w+)*'
        outputs = r'\.outputs \w+( \w+)*'

        header = r'{}\n'.format('\n'.join([declaration, inputs, outputs]))

        # Body
        mask = r'([01-]+  [01]\n)+'
        logic_gate_header = r'\.names \w+([ ]{1,2}\w+)*'
        logic_gate = r'{}\n{}'.format(logic_gate_header, mask)

        body = r'({})+'.format(logic_gate)

        # End
        end = r'\.end'

        # Whole blif file
        model = r'{}{}{}'.format(header, body, end)
        blif_regex = compile(r'({0}\n)*{0}'.format(model))
        if fullmatch(blif_regex, filtered_text) is None:
                raise Exception('Unsupported blif format')

        self.model = Model().parse(filtered_text)
        return self

    def extract(self, variable):
        outputs = self.model.outputs
        if not variable in outputs:
            raise Exception('{} is not output variable'.format(variable))
        return str(outputs[variable])
