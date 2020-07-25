import pytest

from weeklyreviewtodotxt.prompter import Phase

class DummyPhase(Phase):
    @property
    def prompt(self) -> str:
        return "What do"

@pytest.fixture()
def dp():
    return DummyPhase()

def test_phase_can_give_prompt(dp, capsys):
    for cycle in dp:
        pass
    assert "What do" in capsys.readouterr().out

def test_phase_can_skip_cylce(dp, capsys):
    for cycle in dp:
        pass
    assert "What do" in capsys.readouterr().out
