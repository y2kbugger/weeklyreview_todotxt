import re

datestamp = re.compile(r"^\d\d\d\d-\d\d-\d\d")


class Line():
    def __init__(self, line):
        self.line = line

        self.completed = self.line[0:2] == "x "
        if self.completed:
            self.line = self.line[2:]
        r = datestamp.match(self.line)
        if r is not None:
            self.creation_stamp = r.group()
            self.line = self.line[11:]

    def complete(self, completed=True):
        self.completed = completed

    def creation_date(self, datestamp):
        self.creation_stamp = datestamp

    def persist(self):
        result = []
        if self.completed:
            result.append('x')
        try:
            result.append(self.creation_stamp)
        except:
            pass
        result.append(self.line)
        return ' '.join(result)
