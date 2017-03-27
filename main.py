import argparse
from blifparse import Parser
import pprint
pp = pprint.PrettyPrinter(indent=4)

class Mapper:
    def __getitem__(self, *args):
        return False

def main(filename):
    p = Parser()
    with open(filename) as f:
        parseResult = p.parse(f)

    input_values = Mapper()

    for model in parseResult:
        for output, equation in model.equation().items():
            print(output, '=', repr(equation))
            print(output, '=', equation.evaluate(input_values))
#    print(parseResult)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse blif file.')
    parser.add_argument('filename', metavar='filename', type=str,
                        help='filename of blif file')

    args = parser.parse_args()
    filename = args.filename
    main(filename)
