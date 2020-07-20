from weeklyreviewtodotxt.parser import Task
from weeklyreviewtodotxt.tasktoprojects import convert_task_to_project

from test_parser import assert_tasks_equal

# def test_turn_task_into_project():
#     t = Task("earn degree")
#     convert_task_to_project(t)
#     assert_tasks_equal(t, Task("prj:earn_degree @@@project"))
