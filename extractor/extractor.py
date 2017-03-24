from re import compile, fullmatch
from .utils import without_emptys

from .model import Model
from .logicgate import LogicGate

class Extractor:
    def parse(self, raw_text):
        # Filter lines
        is_valid = lambda l: len(l) > 0 and l[0] != '#'
        lines_without_comments = [line for line in raw_text.split('\n')
                                  if is_valid(line)]
        filtered_text = '\n'.join(lines_without_comments)

        regexps = {}
        def define(name, regexp, wrap=True):
            if wrap:
                regexps[name] = regexp.format(**regexps)
            else:
                regexps[name] = regexp

        define('w', r'\w+')
        define('wht', r'[ ]{1,2}', False)

        # Header
        define('declaration', r'\.model{wht}{w}')
        define('inputs', r'\.inputs{wht}{w}({wht}{w})*')
        define('outputs', r'\.outputs{wht}{w}({wht}{w})*')

        define('header', r'{declaration}\n{inputs}\n{outputs}\n')

        # Body
        define('gate_header', r'\.names{wht}{w}({wht}{w})*')
        define('mask', r'([01-]+{wht}[01]\n)+')
        define('logic_gate', r'{gate_header}\n{mask}')

        define('assignment', r'{w}={w}')
        define('formal_list', r'{assignment}({wht}{assignment})*')
        define('library_gate', r'\.gate{wht}{w}{wht}{formal_list}\n')

        define('latch', r'\.latch{wht}{w}{wht}{w}{wht}re{wht}{w}{wht}2\n')

        define('body', r'(({logic_gate})|({latch}))+')

        # End
        define('end', r'\.end')

        # Whole blif file
        define('model', r'{header}{body}{end}')
        define('blif', r'({model}\n)*{model}')
        blif_regexp = compile(regexps['blif'])

        def fail(err=''):
            unsprrt_err = 'Unsupported blif format: '
            raise Exception(unsprrt_err + err)

        if fullmatch(blif_regexp, filtered_text) is None:
            fail('Doesn\'t match regular expression')

        models = {}
        for model_text in without_emptys(filtered_text.split('.end')):
            model = Model().parse(model_text.strip())
            if model.name in models:
                fail('File has two or models with the same name: ' + mode.name)
            models[model.name] = model
        self.models = models

        return self

    def extract(self, name, node):
        return '{} = '.format(name) + str(node)

    def extract_all(self):
        result = ''
        for model in self.models.values():
            result += '\n'.join([self.extract(model.name + '.' + name, node)
                                 for name, node in model.outputs.items()])
        return result
