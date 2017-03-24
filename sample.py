from extractor import Extractor as E
from sys import argv

filename = argv[1]

e = E()
with open(filename) as f:
    e.parse(f.read(), print)
    print(e.extract_all())
