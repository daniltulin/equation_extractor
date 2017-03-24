from .utils import without_emptys
from .node import Node
from .logicgate import LogicGate
from .librarygate import LibraryGate

class Model:
    def __init__(self):
        self.name = None
        self.inputs = None
        self.outputs = None
        self.logic_gates = None

    def parse(self, text):
        lines = text.split('\n')

        # Take components of blif file
        model_token, input_token, output_token = lines[0:3]
        content = lines[3:]

        self.name = model_token.split()[1]
        # Inputs and outputs section
        _, input_names_text = input_token.split('.inputs')
        input_names = input_names_text.split()

        _, output_names = output_token.split('.outputs')

        self.outputs = {name: Node(name) for name in output_names.split()}

        filter_content = lambda f: [l for l in content if f(l)]

        dependencies = {}

        # Content section
        is_latch = lambda line: line.split()[0] == '.latch'
        is_library_gate = lambda line: line.split()[0] == '.gate'
        is_logic_gate = lambda l: not is_latch(l) and not is_library_gate(l)

        # Latchs
        latchs = filter_content(is_latch)
        latch_output_name = lambda l: l.split()[2]
        input_names += [latch_output_name(l) for l in latchs]

        # Library gates
        library_lines = filter_content(is_library_gate)
        self.library_gates = [LibraryGate().parse(t) for t in library_lines]

        # Logic Gates
        reminder = filter_content(is_logic_gate)
        text_logic_gates = without_emptys('\n'.join(reminder).split('.names '))

        logic_gates = []

        inputs = {}
        for text_gate in text_logic_gates:
            gate_lines = text_gate.split('\n')
            if len(gate_lines) == 2:
                header, mask = gate_lines
                name = header.strip()
                stripped_mask = mask.strip()
                if stripped_mask == '-':
                    input_names.append(name)
                    continue
                elif len(stripped_mask) == 1:
                    value = int(mask.strip())
                    inputs[name] = Node(name, value=value)
                    continue
            logic_gates.append(LogicGate().parse(text_gate))

        for gate in logic_gates:
            dependencies[gate.output_name] = gate

        self.inputs = {**{name: Node(name) for name in input_names},
                       **inputs}
        self.dependencies = dependencies

        return self

    def map_models(self, models):
        for gate in self.library_gates:
            gate.map_model(models[gate.model_name])
            for output_name in gate.output_names:
                self.dependencies[output_name] = gate

        for output_node in self.outputs.values():
            self.build_dependencies(output_node)

    def build_dependencies(self, node):
        if node.name in self.inputs:
            return
        gate = self.dependencies[node.name]
        node.dep = gate
        for input_node in gate.input_nodes:
            self.build_dependencies(input_node)

    def __str__(self):
        input_text = 'input  variables: ' + \
                     ', '.join([name for name in self.inputs])
        output_text = 'output variables: ' + \
                      ', '.join([name for name in self.outputs])
        name = 'name: ' + self.name
        size = len(name)
        indent = ''.join([' '] * size)
        return '\n'.join([name, indent + input_text, indent + output_text])
