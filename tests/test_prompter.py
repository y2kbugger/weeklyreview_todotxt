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

@pytest.fixture()
def out(capsys):
    return lambda:capsys.readouterr().out

def test_no_prompt_if_no_tasks(dp, out):
    for cycle in dp:
        pass
    assert out().count("What do") == 0

def test_phase_can_skip_cycle(dp, out, tasks : Tasks, capsys):
    tasks.add_task(Task(""))
    dp.add_input(['s'])
    for cycle in dp:
        pass
    o = out()
    assert o.count("What do") == 1
    assert o.count("Skipping") == 1

def test_input_consumed_fifo(dp):
    dp.add_input(['s'])
    dp.add_input(['s2'])
    assert dp.next_response() == 's'
    assert dp.next_response() == 's2'

def test_asks_for_user_input_if_responses_run_dry(dp):
    dp.add_input(['s'])
    assert dp.next_response() == 's'
    with pytest.raises(IOError):
        dp.next_response()

def test_displays_options_command(dp, out, tasks):
    tasks.add_task(Task(""))
    with pytest.raises(IOError):
        for cycle in dp:
            pass
    assert out().count('skip') == 1
