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
    l.persist() == "x c"

def test_can_uncomplete():
    l = Line("x c")
    l.complete(False)
    l.persist() == "c"

# def test_can_add_date():
#     l = Line("c")
#     l.creation_date("2015-01-27")
#     l.persist() == "c"
