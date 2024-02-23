import pytest

from weeklyreviewtodotxt.weeklyreviewsession import Tasks, Task
from weeklyreviewtodotxt.prompter import Phase, Option, FixLegacyProjectPhase, AssignTasksToProjects

from test_weeklyreviewsession import tasks, wr
from test_prompter import DummyPhaseInput, out

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

def test_flp_manual_has_correct_effect(flp_dp, tasks:Tasks, out):
    flp_dp.dummy_input = ['m', 'mars_attacks']
    tasks.add_task(t:=Task("@@@project test"))
    next(flp_dp)
    assert t.persist == '@@@project test prj:mars_attacks'

### AssignTasksToProject
@pytest.fixture()
def attp_dp(tasks, wr):
    class ATTPDP(DummyPhaseInput, AssignTasksToProjects):
        pass
    dp = ATTPDP(weeklyreview=wr)
    dp.dummy_tasks = tasks
    return dp

def test_attp_prompts_projects(attp_dp, tasks, out):
    tasks.add_task(Task("unassigned_task"))
    tasks.add_task(Task("@@@project prj:fakeproj1"))
    tasks.add_task(Task("an assigned task prj:fakeproj2"))
    with pytest.raises(IOError):
        next(attp_dp)
    o = out()
    print(o)
    assert 'auto create' in o
    assert 'new project' in o
    assert '0. fakeproj1' in o

def test_attp_auto_has_correct_effect(attp_dp, tasks, out):
    attp_dp.dummy_input = ['a']
    tasks.add_task(t:=Task("make thing"))
    next(attp_dp)
    assert t.persist == 'prj:make_thing @@@project'
    print(out())

def test_attp_new_test_makes_new_and_assigns(attp_dp, tasks, out):
    attp_dp.dummy_input = ['n','new']
    tasks.add_task(t:=Task("make thing"))
    next(attp_dp)
    assert t.persist == 'make thing prj:new'
    assert Task('prj:new @@@project') in tasks

def test_attp_can_assign_to_existing_prj(attp_dp, tasks, out):
    attp_dp.dummy_input = ['p','0']
    tasks.add_task(t:=Task("buy paint"))
    tasks.add_task(Task("@@@project prj:guitar"))
    next(attp_dp)
    assert t.persist == "buy paint prj:guitar"
