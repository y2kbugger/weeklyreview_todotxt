from .parser import Task, Generic

def convert_task_to_project(task : Task):
    first_generic = [p for p in task.parts if type(p) is Generic][0]
    task.remove_part(first_generic.persist)
    task.add_part("prj:" + first_generic.persist.replace(' ', '_'))
    task.add_part("@@@project")

