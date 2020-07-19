import re
from datetime import date



class Line():
    def __init__(self, line):
        self.parts = self.parse_line(line)

    def __eq__(self, o):
        if not isinstance(o, Line):
            return False
        print(sorted(self.parts),sorted(o.parts))
        return sorted(self.parts) == sorted(o.parts)

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

    @property
    def dates(self):
        return [p for p in self.parts if isinstance(p, Date)]

    @property
    def creation_date(self):
        if len(self.dates) == 1:
            return self.dates[0].date
        elif len(self.dates) == 2:
            return self.dates[1].date
        else:
            raise ValueError("Weird amount of dates")

    @property
    def completion_date(self):
        if len(self.dates) == 1:
            return None
        elif len(self.dates) == 2:
            return self.dates[0].date
        else:
            raise ValueError("Weird amount of dates")

    def persist(self):
        print(self.parts)
        return ' '.join(p.persist() for p in self.parts)


class Part():
    def __init__(self, string):
        self.string = string

    def __lt__(self, o):
        return self.persist() < o.persist()

    def __eq__(self, o):
        return self.persist() == o.persist()

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

    def persist(self):
        return self.date.isoformat()

def make_part(i, string):
    if i == 0 and Completed.match(string):
        return Completed(string)

    for PartClass in [Date, Part]:
        if PartClass.match(string):
            return PartClass(string)

    assert False, "must match one of these"
