from pathlib import Path
from datetime import date

from weeklyreviewtodotxt.parser import Task, Date, Completed, Generic

def assert_unchanged(line):
    assert Task(line).persist == line.strip()

def assert_tasks_equal(task1, task2):
    assert sorted(task1.parts) == sorted(task2.parts)

def assert_tasks_not_equal(task1, task2):
    assert sorted(task1.parts) != sorted(task2.parts)

def test_empty_line():
    assert_unchanged("")

def test_single_char():
    assert_unchanged("c")

def test_completed():
    assert_unchanged("x c")

def test_can_complete():
    l = Task("c")
    l.complete()
    assert l.persist == "x c"

def test_can_uncomplete():
    l = Task("x c")
    l.uncomplete()
    assert l.persist == "c"

def test_can_have_date():
    assert_unchanged("x 2015-01-27 c")

def test_can_get_creation_date():
    l = Task("x 2015-01-27 c")
    assert l.creation_date == date(2015,1,27)

def test_knows_when_completion_date_is_none():
    l = Task("x 2015-01-27 c")
    assert l.completion_date == None

def test_can_get_creation_date_when_also_completed():
    l = Task("x 2015-02-05 2015-01-27 c")
    assert l.creation_date == date(2015,1,27)

def test_can_get_completion_date():
    l = Task("x 2015-02-05 2015-01-27 c")
    assert l.completion_date == date(2015,2,5)

def test_can_get_contexts():
    t = Task("@home b c +mytag @whoa")
    contexts = {c.persist for c in t.contexts}
    assert {"@home", "@whoa"} == contexts

def test_can_get_extensions():
    t = Task("@home b c h:1 +mytag @whoa")
    extension = t.extensions['h']
    assert "h:1" == extension.persist

def test_can_get_extensions_values():
    t = Task("@home b c h:1 +mytag @whoa")
    extension = t.extensions['h']
    assert "1" == extension.value

def test_empty_priority_is_none():
    t = Task("@home b c h:1 +mytag @whoa")
    assert t.priority is None

def test_can_get_priority():
    t = Task("(A) @home b c h:1 +mytag @whoa")
    assert "A" == t.priority.value
    assert "(A)" == t.priority.persist

def test_part_repr():
    assert repr(Generic("lol###")) == "Generic('lol###')"

def test_date_repr():
    assert repr(Date("2015-11-22")) == "Date('2015-11-22')"

def test_can_evaluate_equality():
    t1 = Task("c +mytag")
    t2 = Task("+mytag c")
    t3 = Task("+mytag d")
    assert_tasks_equal(t1, t2)
    assert_tasks_not_equal(t1, t3)

def test_generic_words_must_stay_as_lumps_for_equality():
    t1 = Task("a b")
    t2 = Task("b a")
    assert_tasks_not_equal(t1, t2)

def test_tags_can_separate_lumps():
    t1 = Task("a +mytag b c")
    t2 = Task("b c +mytag a")
    assert_tasks_equal(t1, t2)

def test_contexts_can_separate_lumps():
    t1 = Task("a @home b c")
    t2 = Task("b c @home a")
    assert_tasks_equal(t1, t2)

def test_extensions_can_separate_lumps():
    t1 = Task("a prj:myprj b c")
    t2 = Task("b c prj:myprj a")
    assert_tasks_equal(t1, t2)

def test_cant_add_tag_twice():
    initial = Task("x 2015-02-05 2015-01-27 c +mytag")
    target = Task("x 2015-02-05 2015-01-27 c +mytag")
    initial.add_part('+mytag')
    assert_tasks_equal(initial, target)

def test_can_add_tag():
    initial = Task("x 2015-02-05 2015-01-27 c")
    target = Task("x 2015-02-05 2015-01-27 c +mytag")
    initial.add_part('+mytag')
    assert_tasks_equal(initial, target)

def test_can_remove_part():
    initial = Task("x 2015-02-05 2015-01-27 c +mytag")
    target = Task("x 2015-02-05 2015-01-27 +mytag")
    initial.remove_part('c')
    assert_tasks_equal(initial, target)

def test_against_legacy():
    with open(Path(__file__).parent / 'todo.txt') as f:
        for line in f.readlines():
            assert_unchanged(line)
