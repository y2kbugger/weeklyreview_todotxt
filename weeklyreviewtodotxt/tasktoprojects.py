from .parser import Task, Generic

class TasksToProjects:
    def __init__(self):
        self.tasks = []

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
        self.tasks.append(task)

    def there_are_duplicates(self):
        return len(set(self.tasks)) != len(self.tasks)

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
    ttp = TasksToProjects()
    with open('/home/y2k/devel/weeklyreview_todotxt/tests/todo.txt') as f:
        for line in f.readlines():
            ttp.add_task(Task(line))

    if ttp.there_are_duplicates():
        print('Cannot act on a file containing duplicates')
        return

    for t in ttp.dailyreview_tasks:
        print(t.persist)

if __name__ == '__main__':
    main()
