from weeklyreviewtodotxt.parser import parse_line
def test_empty_line():
    assert parse_line("").persist() == ""
