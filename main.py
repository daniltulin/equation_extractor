from extractor import Extractor as E

e = E()

with open('b1.blif') as f:
    e.parse(f.read())
print(e.extract('pf'))
