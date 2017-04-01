from .pyparsing import Word, OneOrMore, Suppress, alphanums, alphas
from .pyparsing import StringEnd, Optional, ParserElement, Group

from .components import LogicGate, LibraryGate, Variable, InputVariable,\
                        ConstantVariable, Bit, Bits, Latch, Model

class Parser():
    def parse(self, f):
        is_valuable_line = lambda l: len(l) > 0 and l[0] != '#'
        filtered_lines = [l for l in f if is_valuable_line(l)]
        text = ' '.join(filtered_lines).replace('\\', ' ')

        plain_name = Word(alphas + '_', alphanums + '_')
        identifier = plain_name.copy()

        model_name = Suppress('.model') + plain_name('name')

        identifier.setParseAction(Variable.Factory)
        identifier_list = OneOrMore(identifier)

        input_variable = plain_name.copy()
        input_variable.setParseAction(InputVariable.Factory)
        input_variable_list = OneOrMore(input_variable)

        input_list = Suppress('.inputs') + Group(input_variable_list)('inputs')
        output_list = Suppress('.outputs') + Group(identifier_list)('outputs')

        model_declaration = model_name + input_list + output_list

        variable_list = (identifier + Optional(identifier_list))

        bit = Word('01-', max=1)('output_bit')
        mask = Word('01-')('mask')

        bit.setParseAction(Bit.Factory)
        mask.setParseAction(Bits.Factory)

        output_cover = Group((mask + bit) | bit)
        output_covers = OneOrMore(output_cover)

        logic_gate = Suppress('.names') + Group(variable_list)('variables') +\
                     Group(output_covers)('covers')
        logic_gate.setParseAction(LogicGate.Factory)

        identifier_idc = Suppress(identifier)
        latch_variable_list = identifier_idc + plain_name('output')
        type_control_state = Suppress('re') + identifier_idc + Suppress('2')
        latch = Suppress('.latch') + latch_variable_list + type_control_state
        latch.setParseAction(Latch.Factory)

        formal_actual = Group(plain_name('formal') + Suppress('=') +
                              plain_name('actual'))
        assignments = Group(OneOrMore(formal_actual))
        library_gate = (Suppress('.gate') | Suppress(' .subckt')) +\
                       plain_name('model_name') + assignments('assignments')
        library_gate.setParseAction(LibraryGate.Factory)

        component = logic_gate | library_gate | latch

        end = Suppress('.end')
        model = model_declaration + OneOrMore(component)('components') + end
        model.setParseAction(Model.Factory)

        stringEnd = StringEnd()
        blif = OneOrMore(model) + stringEnd

        result = blif.parseString(text)

        models = {m.name: m for m in result}
        for model in models.values():
            model.link_with(models)

        return result
