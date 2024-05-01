import abc

from insync.listregistry import UndoView
from insync.listview import ListView


class Renderer(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def render(listview: ListView, undoview: UndoView) -> str:
        pass
