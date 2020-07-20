from .parser import Task, Generic

class TasksToProjects:
    def __init__(self):
        self.tasks = []

    @property
    def dailyreview_tasks(self):
        def is_part_of_dailyreview(t):
            for c in t.contexts:
                if c.persist[:2] in ['@@', '@^', '@~']:
                    return False
            return True
        return [t for t in self.tasks if is_part_of_dailyreview(t)]

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

def main():
    pass
    # init from file
    # create TTP

