from abc import ABC, abstractmethod

class Tool(ABC):
    def __init__(self, canvas_view):
        self.view = canvas_view
        self.scene = canvas_view.scene

    @abstractmethod
    def mouse_press(self, event):
        pass

    @abstractmethod
    def mouse_move(self, event):
        pass

    @abstractmethod
    def mouse_release(self, event):
        pass