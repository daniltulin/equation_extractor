from .node import Node

class LibraryGate:
    def parse(self, text):
        tokens = text.split()
        self.model_name = tokens[1]
        formal_list = tokens[2:]
        splitted_list = [l.split('=') for l in formal_list]
        self.mapping = {formal: actual for formal, actual in splitted_list}
        self.rev_mapping = {actual: formal for formal, actual in splitted_list}
        return self

    def map_model(self, model):
        mapped_inputs = [self.mapping[name] for name in model.inputs]
        self.input_nodes = [Node(name) for name in mapped_inputs]

        mapped_outputs = [self.mapping[name] for name in model.outputs
                          if name in self.mapping]
        self.output_names = [name for name in mapped_outputs]
        self.model = model

        self.actual_nodes = {self.rev_mapping[node.name]: node
                        for node in self.input_nodes}

    def expand(self, variable):
        formal_equation = str(self.model.outputs[self.rev_mapping[variable]])
        return formal_equation.format(**self.actual_nodes)
