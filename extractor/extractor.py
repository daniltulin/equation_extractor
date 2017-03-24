from re import compile, fullmatch

from .model import Model
from .logicgate import LogicGate

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
