import argparse
from blifparse import Parser

def main(filename):
    p = Parser()
    with open(filename) as f:
        p.parse(f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse blif file.')
    parser.add_argument('filename', metavar='filename', type=str,
                        help='filename of blif file')

    args = parser.parse_args()
    filename = args.filename
    main(filename)

