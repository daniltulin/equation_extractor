from .equation import InputVariable, ConstantVariable
from .bits import Bits
from .equation import Equation

class LogicGate():
    def __init__(self, inputs, output, masks, output_mask):
        self.inputs = inputs
        self.outputs = [output]
        self.masks = masks
        self.output_mask = output_mask

    def __repr__(self):
        return 'Logic gate: inputs: ' + repr(self.inputs) + ', output: ' +\
                self.outputs[0] + ', masks: ' + repr(self.masks) +\
                ', output_mask: ' + repr(self.output_mask)

    def and_equation_for(self, mask):
        equation = Equation()
        components = [(bit, input_var)\
                      for bit, input_var in zip(mask, self.inputs)
                      if not bit.value is None]
        for bit, var in components:
            equation.AND(var.get_equation(), bit)
        return equation

    def equation_for(self, variable_name):
        equation = Equation()
        for mask, bit in zip(self.masks, self.output_mask):
            equation.OR(self.and_equation_for(mask), bit)
        return equation

    @staticmethod
    def Factory(result):
        variables = result.variables
        inputs = variables[:-1]
        output = variables[-1]

        covers = result.covers

        if len(inputs) == 0:
            bit = covers[0].output_bit
            if bit.value is None:
                return InputVariable(output.name)
            else:
                return ConstantVariable(output.name, bit)

        masks = [cover.mask for cover in covers]
        output_mask = Bits([cover.output_bit for cover in covers])
        return LogicGate(inputs, output.name, masks, output_mask)
