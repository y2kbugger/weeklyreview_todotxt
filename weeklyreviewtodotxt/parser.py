import re
from datetime import date



class Line():
    def __init__(self, line):
        self.parts = self.parse_line(line)

    def parse_line(self, line):
        parts = []
        for i, s in enumerate(line.split()):
            parts.append(make_part(i, s))
        return parts

    def complete(self):
        if not isinstance(self.parts[0], Completed):
            self.parts.insert(0, Completed('x'))

    def uncomplete(self):
        if isinstance(self.parts[0], Completed):
            self.parts.pop(0)

    def creation_date(self, date):
        dates = [p for p in self.parts if isinstance(p, Date)]
        assert len(dates) == 1
        dates[0].set_date(date)

    def persist(self):
        print(self.parts)
        return ' '.join(p.persist() for p in self.parts)


class Part():
    def __init__(self, string):
        self.string = string

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.persist())})"

    @staticmethod
    def match(string):

        return True

    def persist(self):
        return self.string

class Completed(Part):
    @staticmethod
    def match(string):
        return string == 'x'

class Date(Part):
    datestamp = re.compile(r"^\d\d\d\d-\d\d-\d\d$")
    def __init__(self, string):
        self.date = date.fromisoformat(string)

    @staticmethod
    def match(string):
        r = Date.datestamp.search(string)
        return (r is not None)

    def set_date(self, date):
        self.date = date

    def persist(self):
        return self.date.isoformat()

def make_part(i, string):
    if i == 0 and Completed.match(string):
        return Completed(string)

    for PartClass in [Date, Part]:
        if PartClass.match(string):
            return PartClass(string)

    assert False, "must match one of these"
