from datetime import date
from weeklyreviewtodotxt.parser import Line

def assert_unchanged(line):
    assert Line(line).persist() == line

def test_empty_line():
    assert_unchanged("")

def test_single_char():
    assert_unchanged("c")

def test_completed():
    assert_unchanged("x c")

def test_can_complete():
    l = Line("c")
    l.complete()
    assert l.persist() == "x c"

def test_can_uncomplete():
    l = Line("x c")
    l.uncomplete()
    assert l.persist() == "c"

def test_can_have_date():
    assert_unchanged("x 2015-01-27 c")

def test_can_set_date():
    l = Line("x 2015-01-27 c")
    l.creation_date(date(2015,1,22))
    assert l.persist() == "x 2015-01-22 c"
