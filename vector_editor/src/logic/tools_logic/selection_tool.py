from src.logic.tools_logic.tools import Tool
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt

class SelectionTool(Tool):
    def mouse_press(self, event):
        QGraphicsView.mousePressEvent(self.view, event)

        if self.view.scene.itemAt(self.view.mapToScene(event.pos()), self.view.transform()):
            self.view.setCursor(Qt.ClosedHandCursor)

    def mouse_move(self, event):
        QGraphicsView.mouseMoveEvent(self.view, event)

        item = self.view.itemAt(event.pos())

        if not (event.buttons() & Qt.LeftButton):
            if item:
                self.view.setCursor(Qt.OpenHandCursor)
            else:
                self.view.setCursor(Qt.ArrowCursor)

    def mouse_release(self, event):
        QGraphicsView.mouseReleaseEvent(self.view, event)
        self.view.setCursor(Qt.ArrowCursor)