from pyparsing import Word, OneOrMore, Suppress, alphanums, alphas
from pyparsing import StringEnd, Optional, ParserElement, Group

class BitParser():
    def __init__(self, token):
        self.bits = token[0].split('')

    def parse(self, bit):
        try: return bool(int(bit))
        except: return None

    def parse_bits(self):
        return [self.parse(bit) for bit in self.bits]

class Parser():
    def parse(self, f):
        is_valuable_line = lambda l: len(l) > 0 and l[0] != '#'
        filtered_lines = [l for l in f if is_valuable_line(l)]
        text = ' '.join(filtered_lines).replace('\\', ' ')

        identifier = Word(alphas + '_', alphanums + '_')
        identifier_list = OneOrMore(identifier)

        model_name = Suppress('.model') + identifier('name')
        input_list = Suppress('.inputs') + Group(identifier_list)('inputs')
        output_list = Suppress('.outputs') + Group(identifier_list)('outputs')

        model_declaration = model_name + input_list + output_list

        variable_list = (identifier + Optional(identifier_list))

        bit = Word('01-', max=1)('output_bit')
        mask = Word('01-')('input_bits')
        output_cover = Group(bit | (mask + bit))
        output_covers = OneOrMore(output_cover)

        logic_gate = '.names' + Group(variable_list)('variables') +\
                     Group(output_covers)('masks')

        identifier_idc = Suppress(identifier)
        latch_variable_list = identifier_idc + identifier('output')
        type_control_state = Suppress('re') + identifier_idc + Suppress('2')
        latch = '.latch' + latch_variable_list + type_control_state

        formal_actual = Group(identifier('formal') + Suppress('=') +
                              identifier('actual'))
        formal_list = Group(OneOrMore(formal_actual))
        library_gate = '.gate' + identifier('name') + formal_list('list')

        command = Group(logic_gate) | Group(library_gate) | Group(latch)

        end = Suppress('.end')
        model = model_declaration + Group(OneOrMore(command))('commands') + end

        stringEnd = StringEnd()
        blif = OneOrMore(Group(model)) + stringEnd

        result = blif.parseString(text)
        return result
