class Bit():
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        try:
            return str(int(self.value))
        except:
            return '-'

    @staticmethod
    def Factory(tokens):
        try:
            return Bit(bool(int(tokens[0])))
        except:
            return Bit(None)

class Bits():
    def __init__(self, bits):
        self.bits = bits

    def __repr__(self):
        return ''.join([repr(bit) for bit in self.bits])

    def __iter__(self):
        return iter(self.bits)

    @staticmethod
    def Factory(tokens):
        return Bits([Bit.Factory([t]) for t in tokens[0]])
