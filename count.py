from extractor import Extractor as E
from os import listdir
from os.path import isfile, join

files = [join('blifs', f) for f in listdir('blifs') if isfile(join('blifs', f))]

e = E()
qty = 0

for file in files:
    with open(file) as f:
        try:
            e.parse(f.read())
            qty += 1
        except KeyboardInterrupt:
            break
        except:
            print(file)
print(qty)
