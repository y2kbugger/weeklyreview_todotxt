import pytest

from weeklyreviewtodotxt.tasktoprojects import Tasks, Task
from weeklyreviewtodotxt.prompter import Phase
from test_taskstoprojects import tasks

class DummyPhase(Phase):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.dummy_input = []
        self.add_option('kite', lambda t:print('Kit'))
        self.add_option('kitten', lambda t:print('Kitten'))

    @property
    def prompt(self) -> str:
        return "What do"

    @property
    def relevant_tasks(self):
        return list(self.dummy_tasks)

    def next_response(self):
        try:
            return self.dummy_input.pop(0)
        except IndexError:
            raise IOError("Exausted Dummy Input")

@pytest.fixture(scope="function")
def dp(tasks):
    dp = DummyPhase()
    dp.dummy_tasks = tasks
    return dp

@pytest.fixture()
def out(capsys):
    return lambda:capsys.readouterr().out

def test_no_prompt_if_no_tasks(dp, out):
    for cycle in dp:
        pass
    assert out().count("What do") == 0

def test_phase_can_skip_cycle(dp, out, tasks : Tasks, capsys):
    tasks.add_task(Task(""))
    dp.dummy_input = ['skip']
    next(dp)
    o = out()
    assert o.count("What do") == 1
    assert o.count("Skipping") == 1

def test_input_consumed_fifo(dp):
    dp.dummy_input = ['s', 's2']
    assert dp.next_response() == 's'
    assert dp.next_response() == 's2'

def test_dummy_raise_ioerror_when_input_exhausted(dp):
    dp.dummy_input = ['s']
    assert dp.next_response() == 's'
    with pytest.raises(IOError):
        dp.next_response()

def test_displays_options_command(dp, out, tasks):
    tasks.add_task(Task(""))
    with pytest.raises(IOError):
        next(dp)
    assert out().count('skip') == 1

def test_can_retry_response(dp, out, tasks):
    tasks.add_task(Task(""))
    dp.dummy_input = ['d', 'skip']
    next(dp)
    assert out().count("Skipping") == 1

def test_can_match_unique_partial_command(dp, out, tasks):
    tasks.add_task(Task(""))
    dp.dummy_input = ['s']
    next(dp)
    assert out().count("Skipping") == 1

def test_partial_matcher_handle_non_unique_matches(dp, out, tasks):
    tasks.add_task(Task(""))
    dp.dummy_input = ['k']
    with pytest.raises(IOError):
        next(dp)

