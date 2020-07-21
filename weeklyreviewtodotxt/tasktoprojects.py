from collections import OrderedDict
from .parser import Task, Generic

class OrderedSetOfTasks:
    def __init__(self):
        self.dict = OrderedDict()
    def __contains__(self, v):
        return v in self.dict
    def __iter__(self):
        return self.dict.keys().__iter__()
    def add_task(self, task : Task):
        if task not in self:
            self.dict[task] = None

class TasksToProjects:
    def __init__(self):
        self.tasks = OrderedSetOfTasks()

    @property
    def dailyreview_tasks(self):
        return [t for t in self.tasks if self.is_part_of_dailyreview(t)]

    @staticmethod
    def is_part_of_dailyreview(t):
        for c in t.contexts:
            if c.persist[:3] == '@@@':
                return False
            if c.persist[:2] in ['@^', '@~']:
                return False
            if c.persist in ['@@agenda', '@@art', '@@plants', '@@store']:
                # todo: Once i split todo.txt into more files
                # this special case should drop out
                return False
        try:
            # hidden
            if t.extensions['h'].value == '1':
                return False
        except KeyError:
            pass

        return True

    def add_task(self, task : Task):
        self.tasks.add_task(task)

    def convert_task_to_project(self, task : Task):
        first_generic = [p for p in task.parts if type(p) is Generic][0]
        task.remove_part(first_generic.persist)
        task.add_part("prj:" + first_generic.persist.replace(' ', '_'))
        task.add_part("@@@project")

    def assign_task_to_project(self, task : Task, project : str):
        assert project[:4] == 'prj:'
        task.add_part(project)

def main():
    ttp = TasksToProjects()
    with open('/home/y2k/devel/weeklyreview_todotxt/tests/todo.txt') as f:
        for line in f.readlines():
            ttp.add_task(Task(line))

    for t in ttp.dailyreview_tasks:
        print(t.persist)

    # with open('/home/y2k/devel/weeklyreview_todotxt/tests/todo.txt.out','w') as f:
    #     f.writelines(t.persist + '\n' for t in ttp.tasks)

if __name__ == '__main__':
    main()
