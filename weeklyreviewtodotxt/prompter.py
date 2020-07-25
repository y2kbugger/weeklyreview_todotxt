class Phase():
    @property
    def prompt(self) -> str:
        raise NotImplementedError()

    def __iter__(self):
        print(self.prompt)
        yield None
