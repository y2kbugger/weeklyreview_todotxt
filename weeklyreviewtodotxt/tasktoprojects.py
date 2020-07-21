from .parser import Task, Generic

class Tasks:
    def __init__(self):
        self._tasklist = list()
        self._seentasks = set()
    def __contains__(self, v):
        return v in self._tasklist
    def __iter__(self):
        return self._tasklist.__iter__()
    def add_task(self, task : Task):
        if task not in self._seentasks:
            self._tasklist.append(task)
    @property
    def projects(self):
        projects = []
        for t in self._tasklist:
            print(t)
            print([c.persist for c in t.contexts])
            if '@@@project' in {c.persist for c in t.contexts}:
                try:
                    projects.append(t.extensions['prj'].value)
                except KeyError:
                    pass
        return projects

    def make_project_if_doesnt_exist(self, proj):
        pass

    def add_tasks_from_file(self, file):
        for line in file.readlines():
            self.add_task(Task(line))

class TasksToProjects:
    def __init__(self, tasks):
        self._tasks = tasks

    @property
    def dailyreview_tasks(self):
        return [t for t in self._tasks if self.is_part_of_dailyreview(t)]

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

    def convert_task_to_project(self, task : Task):
        first_generic = [p for p in task.parts if type(p) is Generic][0]
        task.remove_part(first_generic.persist)
        task.add_part("prj:" + first_generic.persist.replace(' ', '_'))
        task.add_part("@@@project")

    def assign_task_to_project(self, task : Task, project : str):
        assert project[:4] == 'prj:'
        task.add_part(project)

def main():
    from pathlib import Path
    projdir = Path(__file__).parent.parent
    tasks = Tasks()
    ttp = TasksToProjects(tasks)

    with open(projdir/'tests'/'todo.txt') as f:
        tasks.add_tasks_from_file(f)

    for t in ttp.dailyreview_tasks:
        print(t.persist)

    # with open('/home/y2k/devel/weeklyreview_todotxt/tests/todo.txt.out','w') as f:
    #     f.writelines(t.persist + '\n' for t in ttp._tasks)

if __name__ == '__main__':
    main()
