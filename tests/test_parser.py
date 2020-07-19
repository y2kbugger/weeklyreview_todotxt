from datetime import date

from weeklyreviewtodotxt.parser import Line, Date, Completed, Part

def assert_unchanged(line):
    assert Line(line).persist == line

def test_empty_line():
    assert_unchanged("")

def test_single_char():
    assert_unchanged("c")

def test_completed():
    assert_unchanged("x c")

def test_can_complete():
    l = Line("c")
    l.complete()
    assert l.persist == "x c"

def test_can_uncomplete():
    l = Line("x c")
    l.uncomplete()
    assert l.persist == "c"

def test_can_have_date():
    assert_unchanged("x 2015-01-27 c")

def test_can_get_creation_date():
    l = Line("x 2015-01-27 c")
    assert l.creation_date == date(2015,1,27)

def test_knows_when_completion_date_is_none():
    l = Line("x 2015-01-27 c")
    assert l.completion_date == None

def test_can_get_creation_date_when_also_completed():
    l = Line("x 2015-02-05 2015-01-27 c")
    assert l.creation_date == date(2015,1,27)

def test_can_get_completion_date():
    l = Line("x 2015-02-05 2015-01-27 c")
    assert l.completion_date == date(2015,2,5)

def test_part_repr():
    assert repr(Part("lol###")) == "Part('lol###')"

def test_date_repr():
    assert repr(Date("2015-11-22")) == "Date('2015-11-22')"

def test_can_evaluate_equality():
    l = Line("x 2015-02-05 2015-01-27 c +mytag")
    l2 = Line("x 2015-02-05 2015-01-27 +mytag c")
    l3 = Line("x 2015-02-05 2015-01-27 +mytag d")
    assert l == l2
    assert l != l3

def test_cant_add_tag_twice():
    initial = Line("x 2015-02-05 2015-01-27 c +mytag")
    target = Line("x 2015-02-05 2015-01-27 c +mytag")
    initial.add_part('+mytag')
    assert initial == target

# def test_can_add_tag():
#      initial = Line("x 2015-02-05 2015-01-27 c")
#      target = Line("x 2015-02-05 2015-01-27 c +mytag")
#      initial.add_part('+mytag')
#      assert initial == target


