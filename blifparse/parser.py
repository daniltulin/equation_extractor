from pyparsing import Word, OneOrMore, Suppress, alphanums, alphas
from pyparsing import StringEnd, Optional, ParserElement, Group

class Parser():
    def parse(self, f):
        is_valuable_line = lambda l: len(l) > 0 and l[0] != '#'
        filtered_lines = [l for l in f if is_valuable_line(l)]
        text = ' '.join(filtered_lines).replace('\\', ' ')

        identifier = Word(alphas + '_', alphanums + '_')
        identifier_list = OneOrMore(identifier)

        model_name = Suppress('.model') + identifier_list
        input_list = Suppress('.inputs') + identifier_list
        output_list = Suppress('.outputs') + identifier_list

        model_declaration = model_name + input_list + output_list

        variable_list = identifier + Optional(identifier_list)

        bit = Word('01-', max=1)
        mask = Word('01-')
        output_cover = bit | (mask + bit)
        output_covers = OneOrMore(output_cover)

        logic_gate = Suppress('.names') + variable_list + output_covers

        identifier_idc = Suppress(identifier)
        latch_variable_list = identifier_idc + identifier
        type_control_state = Suppress('re') + identifier_idc + Suppress('2')
        latch = Suppress('.latch') + latch_variable_list + type_control_state

        formal_actual = identifier + '=' + identifier
        formal_list = OneOrMore(formal_actual)
        library_gate = Suppress('.gate') + identifier + formal_list

        command = Group(logic_gate | library_gate | latch)

        end = Suppress('.end')
        model = model_declaration + OneOrMore(command) + end

        stringEnd = StringEnd()
        blif = OneOrMore(Group(model)) + stringEnd

        result = blif.parseString(text)
        return result
