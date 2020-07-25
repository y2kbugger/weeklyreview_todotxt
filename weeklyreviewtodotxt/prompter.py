class Phase():
    def __init__(self):
        self.options = {}
        self.input = []
        self.add_option('skip', lambda t:None)

    def add_option(self, command, action):
        self.options[command] = action

    def add_input(self, responses):
        self.input.extend(responses)

    @property
    def prompt(self) -> str:
        raise NotImplementedError()

    def __iter__(self):
        print(self.prompt)
        yield None
