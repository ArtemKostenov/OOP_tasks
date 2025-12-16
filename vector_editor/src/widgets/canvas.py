from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt, QPointF
from src.logic.shape_logic.factory import ShapeFactory
from src.logic.tools_logic.creation_tool import CreationTool
from src.logic.tools_logic.selection_tool import SelectionTool

class EditorCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        self.setSceneRect(0, 0, 800, 600)
        self.setRenderHint(self.renderHints())
        self.setAlignment(Qt.AlignCenter)
        
        self.scene.setBackgroundBrush(Qt.white)

        self.tools = {
            "select": SelectionTool(self),
            "line": CreationTool(self, "line"),
            "rect": CreationTool(self, "rect"),
            "ellipse": CreationTool(self, "ellipse")
        }

        self.active_tool = self.tools["select"]

    def set_tool(self, tool_name):
        if tool_name in self.tools:
            self.active_tool = self.tools[tool_name]
            print(f"Выбран инструмент: {tool_name}")

    def mousePressEvent(self, event):
        self.active_tool.mouse_press(event)

    def mouseReleaseEvent(self, event):
        self.active_tool.mouse_release(event)

    def mouseMoveEvent(self, event):
        self.active_tool.mouse_move(event)