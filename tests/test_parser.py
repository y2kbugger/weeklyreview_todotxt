from weeklyreviewtodotxt.parser import Line

def test_empty_line():
    assert Line("").persist() == ""
