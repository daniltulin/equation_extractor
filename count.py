from main import main
from os import listdir
from os.path import isfile, join

qty = 0
files = [f for f in listdir('blifs') if isfile(join('blifs', f))]
for f in files:
    try:
        main('blifs/' + f)
        qty += 1
    except Exception as e:
        print(f, e)
print(qty)
