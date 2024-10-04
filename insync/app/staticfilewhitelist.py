import os

from fastapi.staticfiles import StaticFiles


class StaticFilesWithWhitelist(StaticFiles):
    def __init__(self, directory: str, included_extensions: list[str]):
        self.included_extensions = included_extensions
        super().__init__(directory=directory)

    def lookup_path(self, path: str) -> tuple[str, os.stat_result | None]:
        if not any(path.endswith(ext) for ext in self.included_extensions):
            raise FileNotFoundError(404, f"File extension must be one of {','.join(self.included_extensions)}, got {path}")
        return super().lookup_path(path)
