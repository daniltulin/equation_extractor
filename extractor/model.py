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
        content = '\n'.join(lines[3:])

        self.name = model_name.split()[1]

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


