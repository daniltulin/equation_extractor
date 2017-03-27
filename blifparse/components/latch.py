from .equation import InputVariable

class Latch():
    @staticmethod
    def Factory(result):
        return InputVariable(result.output)
