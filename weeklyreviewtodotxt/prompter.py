from .parser import Task
from .tasktoprojects import WeeklyReview, FilterTasks

class Option():
    @property
    def command(self) -> str:
        raise NotImplementedError()
    @property
    def description(self) -> str:
        return ""
    def action(self, wr:WeeklyReview, t:Task, phase):
        pass
    def preview(self, t:Task) -> str:
        return ""

class Skip(Option):
    @property
    def command(self) -> str:
        return 'skip'
    @property
    def description(self) -> str:
        return "Go on to the next Task without processing"
    def action(self, wr:WeeklyReview, t:Task, phase):
        print("Skipping")

class Phase():
    def __init__(self):
        self.current_task_ix = 0
        self._options = [Skip()]

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
    def options(self):
        return {o.command:o for o in self._options}

    def run_prompt_for_task(self, task):
        print(self.prompt, flush=True)
        for o in self._options:
            print(f"  {o.command}: {o.preview(task)}")
        r = self.next_response()
        print("Choice: ", r)

        try:
            option = self.match_option(r)
            option.action(self.weeklyreview, task, self)
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
        self._options = [self.Auto(),self.Manual(),Skip()]

    @property
    def prompt(self) -> str:
        return "@@@Project Task missing `prj:xxx`:"

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
        def action(self, wr:WeeklyReview, t:Task, p:Phase):
            wr.convert_task_to_project(t)
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
            return ""
        def action(self, wr:WeeklyReview, t:Task, p:Phase):
            wr.assign_task_to_project(t, p.next_response())
        def preview(self, t:Task) -> str:
            return f"{t.persist} prj:???"
