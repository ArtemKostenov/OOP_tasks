from src.logic.tools_logic.tools import Tool
from src.logic.commands.commands import MoveCommand
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt

class SelectionTool(Tool):
    def __init__(self, canvas_view, undo_stack):
        super().__init__(canvas_view)
        self.undo_stack = undo_stack

        self.item_positions = {}

    def mouse_press(self, event):
        QGraphicsView.mousePressEvent(self.view, event)

        if self.view.scene.itemAt(self.view.mapToScene(event.pos()), self.view.transform()):
            self.view.setCursor(Qt.ClosedHandCursor)

        self.item_positions.clear()
        for item in self.scene.selectedItems():
            self.item_positions[item] = item.pos()

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

        moved_items = []
        for item, start in self.item_positions.items():
            end = item.pos()
            if end != start:
                moved_items.append((item, start, end))

        if moved_items:
            self.undo_stack.beginMacro("Move Items")

            for item, start, end in moved_items:
                cmd = MoveCommand(item, start, end)
                self.undo_stack.push(cmd)
            self.undo_stack.endMacro()

        self.item_positions.clear()