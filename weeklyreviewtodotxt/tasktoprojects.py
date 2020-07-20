from .parser import Task, Generic

class TasksToProjects:
    def __init__(self):
        self.tasks = []

    def add_task(self, task : Task):
        self.tasks.append(task)

    def convert_task_to_project(self, task : Task):
        first_generic = [p for p in task.parts if type(p) is Generic][0]
        new_task = Task(task.persist)
        new_task.remove_part(first_generic.persist)
        new_task.add_part("prj:" + first_generic.persist.replace(' ', '_'))
        new_task.add_part("@@@project")
        return new_task

    def assign_task_to_project(self, task : Task, project : str):
        new_task = Task(task.persist)
        assert project[:4] == 'prj:'
        new_task.add_part(project)
        return new_task
