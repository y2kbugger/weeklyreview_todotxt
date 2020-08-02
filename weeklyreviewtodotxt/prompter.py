from .parser import Task
from .tasktoprojects import WeeklyReview, FilterTasks

class Option():
    def __init__(self, wr, phase):
        self.wr = wr
        self.phase = phase
    @property
    def command(self) -> str:
        raise NotImplementedError()
    @property
    def description(self) -> str:
        raise NotImplementedError()
    def preview(self, t:Task) -> str:
        raise NotImplementedError()
    def display(self, t:Task):
        if self.preview(t) != "":
            print(f"  {self.command}: {self.preview(t)}")
        else:
            print(f"  {self.command}")
        for i, c in enumerate(self.choices()):
            print(f"    {i}. {c}")
    def action(self, t:Task):
        raise NotImplementedError()
    def choices(self):
        return []

class Skip(Option):
    @property
    def command(self) -> str:
        return 'skip'
    @property
    def description(self) -> str:
        return "Go on to the next Task without processing"
    def preview(self, t:Task) -> str:
        return ""
    def action(self, t:Task):
        print("Skipping")

class Phase():
    def __init__(self, weeklyreview:WeeklyReview=None):
        self.weeklyreview = weeklyreview
        self.current_task_ix = 0
        self._option_classes = []

    def __iter__(self):
        return self

    def __next__(self):
        try:
            current_task = self.relevant_tasks[self.current_task_ix]
        except IndexError:
            raise StopIteration()
        self.run_prompt_for_task(current_task)
        self.current_task_ix += 1

    @property
    def _options(self):
        OPs = self._option_classes + [Skip]
        return [OP(self.weeklyreview, self) for OP in OPs]

    def run_prompt_for_task(self, task):
        print(self.prompt, task, flush=True)
        for o in self._options:
            o.display(task)

        r = self.next_response()
        print("Choice: ", r)

        try:
            option = self.match_option(r)
            option.action(task)
        except KeyError as e:
            print(e.args[0])
            self.run_prompt_for_task(task)

    def match_option(self, r):
        matches = [o for o in self._options if o.command.startswith(r)]
        if len(matches) == 0:
            raise KeyError("No options matched")
        if len(matches) > 1:
            raise KeyError(f"Both {','.join(o.command for o in matches)} matched, be more specific.")
        return matches[0]

    def next_response(self):
        return input()

    @property
    def prompt(self) -> str:
        raise NotImplementedError()

    @property
    def relevant_tasks(self):
        raise NotImplementedError()

class FixLegacyProjectPhase(Phase):
    def __init__(self, weeklyreview:WeeklyReview):
        super().__init__()
        self.weeklyreview = weeklyreview
        self._option_classes = [self.Auto, self.Manual]

    @property
    def prompt(self) -> str:
        return "@@@Project missing `prj:xxx`:"

    @property
    def relevant_tasks(self):
        f = FilterTasks.is_legacy_project
        return self.weeklyreview.tasks_filtered_by(f)

    class Auto(Option):
        @property
        def command(self) -> str:
            return 'auto'
        @property
        def description(self) -> str:
            return "Guess the project tag from the legacy project contents"
        def action(self, t:Task):
            self.wr.convert_task_to_project(t)
        def preview(self, t:Task) -> str:
            nt = Task(t.persist)
            WeeklyReview.convert_task_to_project(None, nt)
            return nt.persist

    class Manual(Option):
        @property
        def command(self) -> str:
            return 'manual'
        @property
        def description(self) -> str:
            return "Supply a new name for the prj tag"
        def action(self, t:Task):
            self.wr.assign_task_to_project(t, self.phase.next_response())
        def preview(self, t:Task) -> str:
            return f"{t.persist} prj:???"

class AssignTasksToProjects(Phase):
    def __init__(self, weeklyreview:WeeklyReview):
        super().__init__()
        self.weeklyreview = weeklyreview
        self._option_classes = [self.Auto, self.Manual, self.AssignToExisting]

    @property
    def prompt(self) -> str:
        return "Task missing `prj:xxx`:"

    @property
    def relevant_tasks(self):
        f = FilterTasks.is_dailyreview
        return self.weeklyreview.tasks_filtered_by(f)

    class Auto(Option):
        @property
        def command(self) -> str:
            return 'auto create'
        @property
        def description(self) -> str:
            return "Turn the task into a project and guess prj: tag."
        def action(self, t:Task):
            self.wr.convert_task_to_project(t)
        def preview(self, t:Task) -> str:
            nt = Task(t.persist)
            WeeklyReview.convert_task_to_project(None, nt)
            return nt.persist

    class Manual(Option):
        @property
        def command(self) -> str:
            return 'new project'
        @property
        def description(self) -> str:
            return ""
        def action(self, t:Task):
            self.wr.assign_task_to_project(t, self.phase.next_response())
        def preview(self, t:Task) -> str:
            return f"{t.persist} prj:???"

    class AssignToExisting(Option):
        @property
        def command(self) -> str:
            return 'pick'
        @property
        def description(self) -> str:
            return ""
        def action(self, t:Task):
            choice = '-1'
            while int(choice) not in range(len(wr._tasks.projects)):
                choice = p.next_response()
            project = wr._task[choice]
            wr.assign_task_to_project(t, project)
        def preview(self, t:Task) -> str:
            return f"{t.persist} prj:???"
            # return "\n".join(
        def choices(self):
            return list(self.wr._tasks.projects)
