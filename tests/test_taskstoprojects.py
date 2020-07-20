from weeklyreviewtodotxt.parser import Task
from weeklyreviewtodotxt.tasktoprojects import convert_task_to_project, assign_task_to_project

from test_parser import assert_tasks_equal

def test_turn_task_into_project():
    t = Task("earn degree")
    new_t = convert_task_to_project(t)
    assert_tasks_equal(t, Task("earn degree"))
    assert_tasks_equal(new_t, Task("prj:earn_degree @@@project"))

# def test_can_assign_to_existing_project():
#     t = Task("research graduate programs")
#     new_t = assign_task_to_project(t, 'prj:earn_degree')
#     assert_tasks_equal(t, Task("research graduate programs"))
#     assert_tasks_equal(new_t, Task("research graduate programs prj:earn_degree"))
