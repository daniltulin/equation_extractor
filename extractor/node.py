class Node:
    def __init__(self, name, dep=None):
        self.name = name
        self.dep = dep
        self.expr = None

    def is_leaf(self):
        return self.dep is None

    def cache(self):
        if self.expr is None:
            self.expr = str(self.dep)
        return self.expr

    def __str__(self):
        if self.is_leaf():
            return self.name
        else:
            return self.cache()
