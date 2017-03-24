from .utils import without_emptys
from .node import Node

def wrap(seq, text):
    if len(seq) > 1:
        return '(' + text + ')'
    return text

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
