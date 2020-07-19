from weeklyreviewtodotxt.parser import Line

def test_empty_line():
    assert Line("").persist() == ""

def test_single_char():
    assert Line("c").persist() == "c"

def test_completed():
    assert Line("x c").persist() == "x c"

def test_can_uncomplete():
    l = Line("x c")
    l.complete(False)
    l.persist() == "c"
