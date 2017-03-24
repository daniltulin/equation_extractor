import argparse
from extractor import Extractor

def main():
    parser = argparse.ArgumentParser(description='Parse blif file.')
    parser.add_argument('filename', metavar='filename', type=str,
                        help='filename of blif file')

    args = parser.parse_args()
    filename = args.filename
    extractor = Extractor()
    with open(filename) as f:
        extractor.parse(f.read())

if __name__ == '__main__':
    main()
