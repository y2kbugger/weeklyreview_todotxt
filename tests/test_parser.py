from weeklyreviewtodotxt.parser import Line

def test_empty_line():
    assert Line("").persist() == ""

def test_single_char():
    assert Line("c").persist() == "c"
