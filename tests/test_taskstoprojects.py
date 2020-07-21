import pytest

from weeklyreviewtodotxt.parser import Task
from weeklyreviewtodotxt.tasktoprojects import TasksToProjects, Tasks

from test_parser import assert_tasks_equal

@pytest.fixture
def tasks():
    return Tasks()

def test_can_get_projects(tasks):
    tasks.add_task(Task("hello prj:lol @@@project"))
    tasks.add_task(Task("world"))
    assert tasks.projects == ['lol']

@pytest.fixture
def ttp():
    ttp = TasksToProjects()
    return ttp

def test_can_add_tasks(ttp):
    ttp.add_task(Task("hello"))
    ttp.add_task(Task("world"))
    assert list(ttp.tasks) == [
        Task("hello"),
        Task("world"),
        ]

def test_can_refine_list_to_daily_review(ttp):
    [ttp.add_task(Task(t)) for t in [
        "be happy @@@project",
        "twist and shout @~music",
        "bak 15r @^chores",
        "rotate peacock h:1",
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
    ttp.convert_task_to_project(t)
    assert_tasks_equal(t, Task("prj:earn_degree @@@project"))

def test_can_assign_to_existing_project(ttp):
    ttp.add_task(Task("prj:earn_degree @@@project"))
    t = Task("research graduate programs")
    ttp.add_task(t)
    ttp.assign_task_to_project(t, 'prj:earn_degree')
    assert list(ttp.tasks) == [
        Task("prj:earn_degree @@@project"),
        Task("research graduate programs prj:earn_degree"),
        ]

# def test_ttp_creates_project_if_doesnt_exist(ttp):
#     ttp.add_task(t:=Task("research graduate programs"))
#     ttp.assign_task_to_project(t, 'prj:earn_degree')
#     assert list(ttp.tasks) == [
#         Task("research graduate programs prj:earn_degree"),
#         Task("prj:earn_degree @@@project"),
#         ]
