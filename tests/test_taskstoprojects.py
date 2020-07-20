from weeklyreviewtodotxt.parser import Task
from weeklyreviewtodotxt.tasktoprojects import convert_task_to_project, assign_task_to_project

from test_parser import assert_tasks_equal

def test_turn_task_into_project():
    t = Task("earn degree")
    convert_task_to_project(t)
    assert_tasks_equal(t, Task("prj:earn_degree @@@project"))

def test_can_assign_to_existing_project():
    t = Task("research graduate programs")
    assign_task_to_project(t, 'prj:earn_degree')
