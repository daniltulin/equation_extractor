import argparse
from blifparse import Parser
import pprint
pp = pprint.PrettyPrinter(indent=4)

def get_binary(x, size):
    representation = '{:b}'.format(x).rjust(size, '0')
    return [bool(int(s)) for s in reversed(representation)]

class CorelationFinder:
    def __init__(self, model):
        self.inputs = model.inputs.keys()
        self.equations = model.equation().items()
        self.size = 2 ** len(self.inputs)

    def calculate(self, equation):
        inputs = self.inputs
        size = self.size
        table = [0] * size
        for i in range(size):
            binary = get_binary(i, size)
            mapping = {l: b for l, b in zip(inputs, binary)}
            value = equation.evaluate(mapping)
            table[i] += value
        return table

    def find_correlation(self):
        size = self.size
        table = [0] * size
        for name, equation in self.equations:
            print(name, '=', repr(equation))
            t = self.calculate(equation)
            for i in range(size): table[i] += t[i]
        R = sum([value if value != 1 else 0 for value in table])
        return  R / size / len(self.equations)

def main(filename):
    p = Parser()
    with open(filename) as f:
        parseResult = p.parse(f)

    for model in parseResult:
        if len(model.input_variables) != 0:
            print(model.name, 'contains sequintial sequential circuit(s)')
            continue
        print(model.name, 'correlation:',
              CorelationFinder(model).find_correlation())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse blif file.')
    parser.add_argument('filename', metavar='filename', type=str,
                        help='filename of blif file')

    args = parser.parse_args()
    filename = args.filename
    main(filename)
