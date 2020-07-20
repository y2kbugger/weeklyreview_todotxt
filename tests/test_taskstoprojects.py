import pytest

from weeklyreviewtodotxt.parser import Task
from weeklyreviewtodotxt.tasktoprojects import TasksToProjects

from test_parser import assert_tasks_equal

@pytest.fixture
def ttp():
    ttp = TasksToProjects()
    return ttp

def test_can_add_tasks(ttp):
    ttp.add_task(Task("hello"))
    ttp.add_task(Task("world"))
    assert ttp.tasks == [
        Task("hello"),
        Task("world"),
        ]

def test_can_refine_list_to_daily_review(ttp):
    [ttp.add_task(Task(t)) for t in [
        "be happy @@@project",
        "twist and shout @~music",
        "bak 15r @^chores",
        "oil basketball",
        "pet cat @@home",
        "paint cat @@art",
        "fix speaker fur prj:boom_box",
        ]]
    assert [t.persist for t in ttp.dailyreview_tasks] == [
        "oil basketball",
        "pet cat @@home",
        "fix speaker fur prj:boom_box"
        ]

def test_turn_task_into_project(ttp):
    t = Task("earn degree")
    new_t = ttp.convert_task_to_project(t)
    assert_tasks_equal(t, Task("earn degree"))
    assert_tasks_equal(new_t, Task("prj:earn_degree @@@project"))

def test_can_assign_to_existing_project(ttp):
    t = Task("research graduate programs")
    new_t = ttp.assign_task_to_project(t, 'prj:earn_degree')
    assert_tasks_equal(t, Task("research graduate programs"))
    assert_tasks_equal(new_t, Task("research graduate programs prj:earn_degree"))

