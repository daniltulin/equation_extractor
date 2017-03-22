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
        return self.dep == None

    def cache(self):
        if self.expr == None:
            self.expr = str(self.dep)
        return self.expr

    def __str__(self):
        if self.is_leaf():
            return self.name
        else:
            return self.cache()

class LogicGate:
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
    def parse(self, text):
        # Filter lines
        not_comment = lambda l: len(l) > 0 and l[0] != '#'
        lines = [line for line in text.split('\n')
                 if not_comment(line)]

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

    def build_dependencies(self, node, depth=0):
        if node.name in self.inputs:
            return
        gate = self.logic_gates[node.name]
        node.dep = gate
        for input_node in gate.input_nodes:
            self.build_dependencies(input_node, depth + 1)

class Extractor:
    def parse(self, text):
        self.model = Model().parse(text)

    def extract(self, variable):
        outputs = self.model.outputs
        if not variable in outputs:
            raise Error('{} is not output variable'.format(variable))
        return str(outputs[variable])
