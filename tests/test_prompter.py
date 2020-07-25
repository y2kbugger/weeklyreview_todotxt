import pytest

from weeklyreviewtodotxt.tasktoprojects import Tasks, Task
from weeklyreviewtodotxt.prompter import Phase
from test_taskstoprojects import tasks

class DummyPhase(Phase):
    @property
    def prompt(self) -> str:
        return "What do"

@pytest.fixture()
def dp(tasks):
    return DummyPhase(tasks)

def test_no_prompt_if_no_tasks(dp, capsys):
    for cycle in dp:
        pass
    out = capsys.readouterr().out
    assert out.count("What do") == 0

def test_phase_can_skip_cycle(dp, capsys, tasks : Tasks):
    tasks.add_task(Task(""))
    dp.add_input(['s'])
    for cycle in dp:
        pass
    assert "What do" in capsys.readouterr().out

def test_input_consumed_fifo(dp):
    dp.add_input(['s'])
    dp.add_input(['s2'])
    assert dp.next_response() == 's'
    assert dp.next_response() == 's2'

# def test_asks_for_user_input_if_responses_run_dry(dp):
#     dp.next_response()

