class Phase():
    def __init__(self, tasks):
        self.tasks = tasks
        self.options = {}
        self.input = []
        self.add_option('skip', lambda t:None)

    @property
    def prompt(self) -> str:
        raise NotImplementedError()

    def __iter__(self):
        for task in self.tasks:
            print(self.prompt)
            yield None

    def add_option(self, command, action):
        self.options[command] = action

    def add_input(self, responses):
        self.input.extend(responses)

    def next_response(self):
        return self.input.pop(0)
