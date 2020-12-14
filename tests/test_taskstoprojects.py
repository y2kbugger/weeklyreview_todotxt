from io import StringIO
import pytest

from weeklyreviewtodotxt.parser import Task
from weeklyreviewtodotxt.weeklyreviewsession import WeeklyReview, Tasks, FilterTasks

from test_parser import assert_tasks_equal

@pytest.fixture
def tasks():
    return Tasks()

def test_can_add_tasks(tasks):
    tasks.add_tasks_from_list(["hello", "world"])
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
    tasks.add_tasks_from_list(["hello", "world"])
    sio = StringIO()
    tasks.persist_task_to_file(sio)
    sio.seek(0)
    assert sio.read() == "hello\nworld\n"

def test_can_get_projects(tasks):
    tasks.add_tasks_from_list([
        "hello prj:lol @@@project",
        "world"])
    assert tasks.projects == ['lol']


def test_can_refine_list_to_daily_review(tasks, wr):
    tasks.add_tasks_from_list([
        "be happy @@@project",
        "twist and shout @~music",
        "bak 15r @^chores",
        "rotate peacock h:1",
        "oil basketball",
        "pet cat @@home",
        "paint cat @@art",
        "fix speaker fur prj:boom_box",
        ])
    f = FilterTasks.is_dailyreview
    assert [t.persist for t in wr.tasks_filtered_by(f)] == [
        "oil basketball",
        "pet cat @@home",
        "fix speaker fur prj:boom_box"
        ]

def test_can_refine_list_projects(tasks, wr):
    tasks.add_tasks_from_list([
        "be happy @@@project",
        "twist and shout @~music",
        "hidden h:1 @@@project",
        ])
    f = FilterTasks.is_project
    assert [t.persist for t in wr.tasks_filtered_by(f)] == [
        "be happy @@@project",
        ]
def test_can_filter_hidden_tasks(tasks, wr):
    tasks.add_tasks_from_list([ "c", "c h:1", "c h:0" ])
    f = FilterTasks.is_hidden
    assert [t.persist for t in wr.tasks_filtered_by(f)] == ["c h:1"]

def test_can_refine_list_prj_tag(tasks:Tasks, wr):
    tasks.add_tasks_from_list([
        "be happy @@@project",
        "prj:twist",
        ])
    f = FilterTasks.by_extension('prj')
    assert [t.persist for t in wr.tasks_filtered_by(f)] == [
        "prj:twist",
        ]

@pytest.fixture
def wr(tasks):
    wr = WeeklyReview(tasks)
    return wr

def test_turn_task_into_project(wr):
    t = Task("earn degree")
    wr.convert_task_to_project(t)
    assert_tasks_equal(t, Task("prj:earn_degree @@@project"))

def test_can_assign_to_existing_project(tasks, wr):
    tasks.add_task(Task("prj:earn_degree @@@project"))
    tasks.add_task(t:=Task("research graduate programs"))
    wr.assign_task_to_project(t, 'earn_degree')
    assert list(tasks) == [
        Task("prj:earn_degree @@@project"),
        Task("research graduate programs prj:earn_degree"),
        ]

def test_wr_creates_project_if_doesnt_exist(tasks, wr):
    tasks.add_task(t:=Task("research graduate programs"))
    wr.assign_task_to_project(t, 'earn_degree')
    assert list(tasks) == [
        Task("research graduate programs prj:earn_degree"),
        Task("prj:earn_degree @@@project"),
        ]
