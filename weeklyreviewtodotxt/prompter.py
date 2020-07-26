class Phase():
    def __init__(self):
        self.current_task_ix = 0
        self.options = {}
        self.add_option('skip', lambda t:print('Skipping'))

    def __iter__(self):
        return self

    def __next__(self):
        try:
            current_task = self.relevant_tasks[self.current_task_ix]
        except IndexError:
            raise StopIteration()
        self.run_prompt_for_task(current_task)
        self.current_task_ix += 1

    def run_prompt_for_task(self, task):
        print(self.prompt, flush=True)
        for o in self.options.keys():
            print(o)
        r = self.next_response()
        print("Choice: ", r)

        try:
            command_key = self.match_option_command(r)
            self.options[command_key](task)
        except KeyError as e:
            print(e.args[0])
            self.run_prompt_for_task(task)

    def match_option_command(self, r):
        matches = [key for key in self.options.keys() if key.startswith(r)]
        if len(matches) == 0:
            raise KeyError("No options matched")
        if len(matches) > 1:
            raise KeyError(f"Both {','.join(matches)} matched, be more specific.")
        return matches[0]


    def add_option(self, command, action):
        self.options[command] = action

    def next_response(self):
        return input()

    @property
    def prompt(self) -> str:
        raise NotImplementedError()

    @property
    def relevant_tasks(self):
        raise NotImplementedError()


# class Option:


