from io import StringIO
import pytest

from weeklyreviewtodotxt.parser import Task
from weeklyreviewtodotxt.tasktoprojects import TasksToProjects, Tasks

from test_parser import assert_tasks_equal

@pytest.fixture
def tasks():
    return Tasks()

def test_can_add_tasks(tasks):
    [tasks.add_task(Task(t)) for t in ["hello", "world", ]]
    assert list(tasks) == [Task("hello"), Task("world")]

def test_can_read_tasks_from_file(tasks):
    sio = StringIO("hello\nworld\n")
    tasks.add_tasks_from_file(sio)
    assert list(tasks) == [Task("hello"), Task("world")]

def test_can_read_tasks_from_file_and_ignore_blankslines(tasks):
    sio = StringIO("hello\n\nworld\n")
    tasks.add_tasks_from_file(sio)
    assert list(tasks) == [Task("hello"), Task("world")]

def test_can_save_tasks_to_file(tasks):
    [tasks.add_task(Task(t)) for t in ["hello", "world", ]]
    sio = StringIO()
    tasks.persist_task_to_file(sio)
    sio.seek(0)
    assert sio.read() == "hello\nworld\n"

def test_can_get_projects(tasks):
    [tasks.add_task(Task(t)) for t in [
        "hello prj:lol @@@project",
        "world"]]
    assert tasks.projects == ['lol']


def test_can_refine_list_to_daily_review(tasks):
    [tasks.add_task(Task(t)) for t in [
        "be happy @@@project",
        "twist and shout @~music",
        "bak 15r @^chores",
        "rotate peacock h:1",
        "oil basketball",
        "pet cat @@home",
        "paint cat @@art",
        "fix speaker fur prj:boom_box",
        ]]
    assert [t.persist for t in tasks.dailyreview_tasks] == [
        "oil basketball",
        "pet cat @@home",
        "fix speaker fur prj:boom_box"
        ]

def test_can_refine_list_projects(tasks):
    [tasks.add_task(Task(t)) for t in [
        "be happy @@@project",
        "twist and shout @~music",
        "hidden h:1 @@@project",
        ]]
    assert [t.persist for t in tasks.project_tasks] == [
        "be happy @@@project",
        ]

def test_can_refine_list_prj_tag(tasks:Tasks):
    [tasks.add_task(Task(t)) for t in [
        "be happy @@@project",
        "prj:twist",
        ]]
    print(tasks.tasks_by_extension)
    assert [t.persist for t in tasks.tasks_by_extension('prj')] == [
        "prj:twist",
        ]

@pytest.fixture
def ttp(tasks):
    ttp = TasksToProjects(tasks)
    return ttp

def test_turn_task_into_project(ttp):
    t = Task("earn degree")
    ttp.convert_task_to_project(t)
    assert_tasks_equal(t, Task("prj:earn_degree @@@project"))

def test_can_assign_to_existing_project(tasks, ttp):
    tasks.add_task(Task("prj:earn_degree @@@project"))
    tasks.add_task(t:=Task("research graduate programs"))
    ttp.assign_task_to_project(t, 'earn_degree')
    assert list(tasks) == [
        Task("prj:earn_degree @@@project"),
        Task("research graduate programs prj:earn_degree"),
        ]

def test_ttp_creates_project_if_doesnt_exist(tasks, ttp):
    tasks.add_task(t:=Task("research graduate programs"))
    ttp.assign_task_to_project(t, 'earn_degree')
    assert list(tasks) == [
        Task("research graduate programs prj:earn_degree"),
        Task("prj:earn_degree @@@project"),
        ]
