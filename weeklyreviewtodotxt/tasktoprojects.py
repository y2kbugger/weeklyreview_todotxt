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
            if '@@@project' in {c.persist for c in t.contexts}:
                try:
                    projects.append(t.extensions['prj'].value)
                except KeyError:
                    pass
        return projects

    @property
    def dailyreview_tasks(self):
        return [t for t in self if self.is_dailyreview_task(t)]

    @property
    def project_tasks(self):
        return [t for t in self if self.is_project_task(t)]

    @staticmethod
    def is_dailyreview_task(t):
        if t.is_hidden():
            return False
        for c in t.contexts:
            if c.persist[:3] == '@@@':
                return False
            if c.persist[:2] in ['@^', '@~']:
                return False
            if c.persist in ['@@agenda', '@@art', '@@plants', '@@store']:
                # todo: Once i split todo.txt into more files
                # this special case should drop out
                return False
        return True

    @staticmethod
    def is_project_task(t):
        if t.is_hidden():
            return False
        return any(c.persist == '@@@project' for c in t.contexts)

    def make_project_if_doesnt_exist(self, proj):
        if proj not in self.projects:
            self.add_task(Task(f"@@@project prj:{proj}"))

    def add_tasks_from_file(self, file):
        for line in file.readlines():
            if len(line.strip()) == 0:
                continue
            self.add_task(Task(line))

    def persist_task_to_file(self, file):
        file.writelines(t.persist + '\n' for t in self)

class TasksToProjects:
    def __init__(self, tasks):
        self._tasks = tasks

    def convert_task_to_project(self, task : Task):
        first_generic = [p for p in task.parts if type(p) is Generic][0]
        task.remove_part(first_generic.persist)
        task.add_part("prj:" + first_generic.persist.replace(' ', '_'))
        task.add_part("@@@project")

    def assign_task_to_project(self, task : Task, project : str):
        task.add_part("prj:" + project)
        self._tasks.make_project_if_doesnt_exist(project)

def main():
    from pathlib import Path
    projdir = Path(__file__).parent.parent
    tasks = Tasks()
    ttp = TasksToProjects(tasks)

    with open(projdir/'tests'/'todo.txt') as f:
        tasks.add_tasks_from_file(f)

    for t in tasks.project_tasks:
        try:
            t.extensions['prj']
            continue
        except KeyError:
            pass
        nt = Task(t.persist)
        ttp.convert_task_to_project(nt)

        print("\n@@@Project Task missing prj:xxx:\n")
        choices = ['1','2','3']
        choice = None
        while choice not in choices:
            print(""+t.persist+"\n", flush=True)
            prompt = ("Options:\n"
                f"\t1. Auto: `{nt.persist}`\n"
                "\t2. Manually enter prj:xxx\n"
                "\t3. skipn\n\n"
                )
            choice = input(prompt)
        if choice == '1':
            ttp.convert_task_to_project(t)
        elif choice == '2':
            ttp.assign_task_to_project(t, input('prj:'))
        elif choice == '3':
            continue


    for t in tasks.dailyreview_tasks:
        choices = ['1','2','3']
        choice = None
        prj_str = '\n'.join([f"\t\t{len(choices)+i}. {p}"for i,p in enumerate(tasks.projects)])
        [choices.append(str(i)) for i,p in enumerate(tasks.projects)]
        while choice not in choices:
            print("\nDaily review Task missing prj:xxx,")
            print("\n\n\n"+t.persist+"\n", flush=True)
            prompt = ("Options:\n"
                "\t1. Turn into a project\n"
                "\t2. Create new project and assign\n\n"
                "\tOr, assign to a project:\n\n"
                f"{prj_str}\n\n"
                "Choice?: "
                )
            choice = input(prompt)

    with open(projdir/'tests'/'todo.txt.out', 'w') as f:
        tasks.persist_task_to_file(f)

if __name__ == '__main__':
    main()
