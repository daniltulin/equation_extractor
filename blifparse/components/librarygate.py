from .equation import Variable

class LibraryGate():
    def __init__(self, model_name, assignments):
        self.model_name = model_name
        self.assignments = assignments

        self.inputs = None
        self.outputs = None
        self.model = None

    def link_with(self, models):
        model = models[self.model_name]
        assignments = self.assignments
        self.inputs = [Variable(assignments[name])
                       for name in model.inputs]
        self.outputs = [assignments[name] for name in model.outputs.keys()]
        self.model = model

    def equation_for(self, variable_name):
        rev_assignments = {actual: formal
                           for formal, actual in self.assignments.items()}
        model = self.model
        formal_output = model.outputs[rev_assignments[variable_name]]

        actual_input = {var.name: var for var in self.inputs}
        mapping = {rev_assignments[name]: actual
                   for name, actual in actual_input.items()}
        return formal_output.equation().substitute(mapping)

    def __repr__(self):
        return 'Library gate: ' + self.model_name + ', ' +\
                ', '.join([formal + '=' + actual
                           for formal, actual in self.assignments.items()])

    @staticmethod
    def Factory(result):
        model_name = result.model_name
        assignments = {assignment.formal: assignment.actual
                       for assignment in result.assignments}
        return LibraryGate(model_name, assignments)
