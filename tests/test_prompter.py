import pytest

from weeklyreviewtodotxt.tasktoprojects import Tasks, Task
from weeklyreviewtodotxt.prompter import Phase, Option, FixLegacyProjectPhase
from test_taskstoprojects import tasks, wr

# Mix-in dummies
class DummyPhaseInput(Phase):
    def __init__(self, *args, **kw):
        self.weeklyreview = None
        super().__init__(*args, **kw)
        self.dummy_input = []

    def next_response(self):
        try:
            return self.dummy_input.pop(0)
        except IndexError:
            raise IOError("Exhausted Dummy Input")

class DummyPhaseTasks(Phase):
    @property
    def prompt(self) -> str:
        return "What do"

    @property
    def relevant_tasks(self):
        return list(self.dummy_tasks)

class DummyOption(Option):
    def __init__(self, command):
        self._dummy_command = command
    @property
    def command(self) -> str:
        return self._dummy_command

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
    dp._options = [DummyOption('kite'),DummyOption('kitten')]
    dp.dummy_input = ['kit']
    with pytest.raises(IOError):
        next(dp)

### Fix Legacy Projects
@pytest.fixture()
def flp_dp(tasks, wr):
    class FLPDP(DummyPhaseInput, FixLegacyProjectPhase):
        pass
    dp = FLPDP(weeklyreview=wr)
    dp.dummy_tasks = tasks
    return dp

def test_flp_filters_to_correct_tasks(flp_dp, tasks):
    tasks.add_tasks_from_list([
        "@@@project test",
        "@@@project prj:test",
        "test"])
    assert list(flp_dp.relevant_tasks) == [
        Task("@@@project test"),
        ]

def test_flp_ask_right_options(flp_dp, tasks, out):
    tasks.add_tasks_from_list([
        "@@@project test"])
    with pytest.raises(IOError):
        next(flp_dp)
    o = out()
    assert o.count('auto') == 1
    assert o.count('manual') == 1
    assert o.count('skip') == 1

def test_flp_auto_give_preview(flp_dp, tasks, out):
    tasks.add_tasks_from_list([
        "@@@project test"])
    with pytest.raises(IOError):
        next(flp_dp)
    assert '@@@project prj:test' in out()

def test_flp_manual_give_preview(flp_dp, tasks, out):
    tasks.add_tasks_from_list([
        "@@@project test"])
    with pytest.raises(IOError):
        next(flp_dp)
    assert '@@@project test prj:???' in out()

def test_flp_auto_has_correct_effect(flp_dp, tasks, out):
    flp_dp.dummy_input = ['a']
    tasks.add_task(t:=Task("@@@project test"))
    next(flp_dp)
    assert t.persist == '@@@project prj:test'

def test_flp_manual_has_correct_effect(flp_dp, tasks, out):
    flp_dp.dummy_input = ['m', 'mars_attacks']
    tasks.add_task(t:=Task("@@@project test"))
    next(flp_dp)
    assert t.persist == '@@@project test prj:mars_attacks'

### AssignTasksToProject
@pytest.fixture()
def flp_dp(tasks, wr):
    class FLPDP(DummyPhaseInput, FixLegacyProjectPhase):
        pass
    dp = FLPDP(weeklyreview=wr)
    dp.dummy_tasks = tasks
    return dp
def assign():
    for t in tasks.dailyreview_tasks:
        choices = ['1','2','3']
        choice = None
        prj_str = '\n'.join([f"\t\t{len(choices)+i}. {p}"for i,p in enumerate(tasks.projects)])
        [choices.append(str(i)) for i,p in enumerate(tasks.projects)]
        while choice not in choices:
            print("\nDaily review Task missing prj:xxx,")
            print("\n\n\n"+t.persist+"\n", flush=True)
            prompt = ("Options:\n"
                "\t1. Turn into a project\n"
                "\t2. Create new project and assign\n\n"
                "\tOr, assign to a project:\n\n"
                f"{prj_str}\n\n"
                "Choice?: "
                )
            choice = input(prompt)
