class Phase():
    def __init__(self, tasks):
        self.tasks = tasks
        self.options = {}
        self.input = []
        self.add_option('skip', lambda t:print('Skipping'))

    @property
    def prompt(self) -> str:
        raise NotImplementedError()

    def __iter__(self):
        for task in self.tasks:
            print(self.prompt, flush=True)
            for o in self.options.keys():
                print(o)
            r = self.next_response()
            try:
                self.options[r](task)
            except KeyError:
                print("Invalid choice, try again")
            yield None

    def add_option(self, command, action):
        self.options[command] = action

    def add_input(self, responses):
        assert all(isinstance(a, str) for a in responses)
        self.input.extend(responses)

    def next_response(self):
        try:
            return self.input.pop(0)
        except IndexError:
            return input()

# class Option:

