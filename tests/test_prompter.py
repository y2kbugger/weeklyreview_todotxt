import pytest

from weeklyreviewtodotxt.tasktoprojects import Tasks, Task
from weeklyreviewtodotxt.prompter import Phase, FixLegacyProjectPhase
from test_taskstoprojects import tasks, wr

# Mix-in dummies
class DummyPhaseInput(Phase):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.dummy_input = []

    @property
    def prompt(self) -> str:
        return "What do"

    def next_response(self):
        try:
            return self.dummy_input.pop(0)
        except IndexError:
            raise IOError("Exhausted Dummy Input")

class DummyPhaseTasks(Phase):
    @property
    def relevant_tasks(self):
        return list(self.dummy_tasks)


@pytest.fixture(scope="function")
def dp(tasks):
    class DP(DummyPhaseTasks, DummyPhaseInput, Phase):
        pass
    dp = DP()
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
    dp.add_option('kite', lambda t:print('Kit'))
    dp.add_option('kitten', lambda t:print('Kitten'))
    dp.dummy_input = ['k']
    with pytest.raises(IOError):
        next(dp)

def legacy():
    for t in tasks.project_tasks:
        try:
            t.extensions['prj']
            continue
        except KeyError:
            pass
        nt = Task(t.persist)
        wr.convert_task_to_project(nt)

        print("\n@@@Project Task missing prj:xxx:\n")
        choices = ['1','2','3']
        choice = None
        while choice not in choices:
            print(""+t.persist+"\n", flush=True)
            prompt = ("Options:\n"
                f"\t1. Auto: `{nt.persist}`\n"
                "\t2. Manually enter prj:xxx\n"
                "\t3. skip\n\n"
                )
            choice = input(prompt)
        if choice == '1':
            wr.convert_task_to_project(t)
        elif choice == '2':
            wr.assign_task_to_project(t, input('prj:'))
        elif choice == '3':
            continue

### Fix Legacy Projects
@pytest.fixture(scope="function")
def flp_dp(tasks, wr):
    class FLPDP(DummyPhaseInput, FixLegacyProjectPhase):
        pass
    dp = FLPDP(weeklyreview=wr)
    dp.dummy_tasks = tasks
    return dp

# def test_flp_filters_to_correct_tasks(flp_dp, tasks:Tasks):
#     tasks.add_tasks_from_list([
#         "@@@project test",
#         "@@@project prj:test",
#         "test"])
#     assert list(flp_dp.relevant_tasks) == [
#         Task("@@@project test"),
#         ]
