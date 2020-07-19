class Line():
    def __init__(self, line):
        self.line = line
        self.completed = self.line[0:2] == "x "
        if self.completed:
            self.line = self.line[2:]

    def complete(self, completed=True):
        self.completed = completed

    def persist(self):
        if self.completed:
            return 'x ' + self.line
        else:
            return self.line
