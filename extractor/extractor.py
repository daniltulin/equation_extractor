from re import compile, fullmatch
from .utils import without_emptys

from .model import Model
from .logicgate import LogicGate

class Extractor:
    def parse(self, raw_text, debug=lambda *args: None):
        # Filter lines
        is_valid = lambda l: len(l) > 0 and l[0] != '#'
        content = [line for line in raw_text.split('\n')
                                  if is_valid(line)]
        debug('Filter text')
        filtered_text = '\n'.join(content)
        debug('Clue text')
        clued_text = filtered_text.replace('\\\n', '')

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
        define('gate_header', r'\.names({wht}{w})+')
        define('mask_with_input', r'(([01-])+{wht}[01]\n)')
        define('mask', r'(({mask_with_input})+|{wht}[01]\n)')
        define('logic_gate', r'{gate_header}\n{mask}')

        define('assignment', r'{w}={w}')
        define('formal_list', r'{assignment}({wht}{assignment})*')
        define('library_gate', r'\.gate{wht}{w}{wht}{formal_list}\n')

        define('latch', r'\.latch{wht}{w}{wht}{w}{wht}re{wht}{w}{wht}2\n')

        define('body', r'(({logic_gate})|({latch})|{library_gate})+')

        # End
        define('end', r'\.end')

        # Whole blif file
        define('model', r'{header}{body}{end}')
        define('blif', r'({model}\n)*{model}')
        blif_regexp = compile(regexps['blif'])

        def fail(err=''):
            unsprrt_err = 'Unsupported blif format: '
            raise Exception(unsprrt_err + err)

        debug('Fullmatching')
        if fullmatch(blif_regexp, clued_text) is None:
            fail('Doesn\'t match regular expression')

        obtained_text = 'Obtained models:'
        self.indent = ''.join([' '] * len(obtained_text))
        debug(obtained_text)

        models = {}

        for model_text in without_emptys(clued_text.split('.end')):
            model = Model().parse(model_text.strip())

            if model.name in models:
                fail('File has two or models with the same name: ' + mode.name)

            models[model.name] = model
            model_description = str(model)
            for d in model_description.split('\n'):
                debug(self.indent +  d)

        for model in models.values():
            model.map_models(models)

        self.models = models

        return self

    def extract(self, name, node, mapping):
        return '{} = '.format(name) + str(node).format(**mapping)

    def extract_model(self, model_name, mapping=None):
        model = self.models[model_name]
        if mapping is None:
            mapping = {name: name for name in model.inputs}
        return '\n'.join([self.extract(name, node, mapping)
                          for name, node in model.outputs.items()])

    def extract_all(self):
        result = ''
        for model_name, model in self.models.items():
            result += self.extract_model(model_name) + '\n'
        return result
