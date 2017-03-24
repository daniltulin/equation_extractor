from .utils import without_emptys
from .node import Node
from .logicgate import LogicGate

class Model:
    def __init__(self):
        self.name = None
        self.inputs = None
        self.outputs = None
        self.logic_gates = None

    def parse(self, text):
        lines = text.split('\n')

        # Take components of blif file
        model_name, input_token, output_token = lines[0:3]
        content = lines[3:]

        self.name = model_name.split()[1]
        # Inputs and outputs section
        _, input_names_text = input_token.split('.inputs')
        input_names = input_names_text.split()

        _, output_names = output_token.split('.outputs')

        self.outputs = {name: Node(name) for name in output_names.split()}

        # Content section
        # Latchs
        is_latch = lambda line: line.split()[0] == '.latch'
        is_logic_gate = lambda line: not is_latch(line)

        latchs = [line for line in content if is_latch(line)]
        latch_output_name = lambda l: l.split()[2]
        input_names += [latch_output_name(l) for l in latchs]
        self.inputs = {name: Node(name) for name in input_names}

        # Logic Gates
        reminder = [l for l in content if is_logic_gate(l)]
        text_logic_gates = without_emptys('\n'.join(reminder).split('.names '))
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


