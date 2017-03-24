def wrap(text):
    return '{' + text + '}'

class Node:
    def __init__(self, name, dep=None, **kwargs):
        self.name = name
        self.dep = dep
        self.expr = None
        self.value = kwargs.get('value', 0)

    def is_leaf(self):
        return self.dep is None

    def cache(self):
        if self.expr is None:
            self.expr = self.dep.expand(self.name)
        return self.expr

    def __repr__(self):
        return '\'Node: ' + self.name + '\''

    def __str__(self):
        if self.is_leaf():
            return wrap(self.name)
        else:
            return self.cache()
