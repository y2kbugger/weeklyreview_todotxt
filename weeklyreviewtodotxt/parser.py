import re
from datetime import date

class Task():
    def __init__(self, line):
        self.parts = self.parse_line(line)

    def __eq__(self, o):
        if not isinstance(o, Task):
            return False
        print(sorted(self.parts),sorted(o.parts))
        return sorted(self.parts) == sorted(o.parts)

    @property
    def dates(self):
        dates =  [p for p in self.parts if isinstance(p, Date)]
        assert 0 < len(dates) <= 2, "Should have at most creation and completion date"
        return dates

    @property
    def creation_date(self):
        if len(self.dates) == 1:
            return self.dates[0].date
        elif len(self.dates) == 2:
            return self.dates[1].date

    @property
    def completion_date(self):
        if len(self.dates) == 1:
            return None
        elif len(self.dates) == 2:
            return self.dates[0].date

    @property
    def persist(self):
        print(self.parts)
        return ' '.join(p.persist for p in self.parts)

    def parse_line(self, line):
        parts = []
        for i, s in enumerate(line.split()):
            try:
                previous_part = parts[-1]
            except:
                previous_part = None
            new_part = make_part(s, i)
            # merge generics together
            if (type(previous_part) is Generic) and type(new_part) is Generic:
                parts[-1] = make_part(previous_part.persist + ' ' + new_part.persist)
            else:
                parts.append(new_part)
        return parts

    def complete(self):
        if not isinstance(self.parts[0], Completed):
            self.parts.insert(0, Completed('x'))

    def uncomplete(self):
        if isinstance(self.parts[0], Completed):
            self.parts.pop(0)

    def add_part(self, part):
        if part in [p.persist for p in self.parts]:
            return
        else:
            self.parts.append(make_part(part))

class Generic():
    def __init__(self, string):
        self.string = string

    def __lt__(self, o):
        return self.persist < o.persist

    def __eq__(self, o):
        return self.persist == o.persist

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.persist)})"

    @staticmethod
    def match(string):
        return True

    @property
    def persist(self):
        return self.string

class Completed(Generic):
    @staticmethod
    def match(string):
        return string == 'x'

class Tag(Generic):
    @staticmethod
    def match(string):
        return string[0] == '+'

class Context(Generic):
    @staticmethod
    def match(string):
        return string[0] == '@'

class Extension(Generic):
    @staticmethod
    def match(string):
        pair = string.split(':')
        if len(pair) != 2:
            return False
        if pair[0] in ['proj', 'rec', 't', 'due']:
            return True
        return False

class Date(Generic):
    datestamp = re.compile(r"^\d\d\d\d-\d\d-\d\d$")
    def __init__(self, string):
        self.date = date.fromisoformat(string)

    @staticmethod
    def match(string):
        r = Date.datestamp.search(string)
        return (r is not None)

    @property
    def persist(self):
        return self.date.isoformat()

def make_part(string, i=None):
    if i == 0 and Completed.match(string):
        return Completed(string)

    for PartClass in [Date, Tag, Context, Extension, Generic]:
        if PartClass.match(string):
            return PartClass(string)

    assert False, "must match one of these"
