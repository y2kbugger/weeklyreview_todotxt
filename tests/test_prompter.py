import pytest

from weeklyreviewtodotxt.prompter import Phase
from test_taskstoprojects import tasks

class DummyPhase(Phase):
    @property
    def prompt(self) -> str:
        return "What do"

@pytest.fixture()
def dp(tasks):
    return DummyPhase()

def test_phase_can_skip_cycle(dp, capsys):
    dp.add_input(['s'])
    for cycle in dp:
        pass
    assert "What do" in capsys.readouterr().out
