from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt, QPointF
from src.logic.shape_logic.factory import ShapeFactory
from src.logic.tools_logic.creation_tool import CreationTool
from src.logic.tools_logic.selection_tool import SelectionTool
from src.logic.shape_logic.group import Group

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

        self.setMouseTracking(True)

    def set_tool(self, tool_name):
        if tool_name in self.tools:
            self.active_tool = self.tools[tool_name]
            print(f"Выбран инструмент: {tool_name}")

            if tool_name == "select":
                self.setCursor(Qt.ArrowCursor)
            else:
                self.setCursor(Qt.CrossCursor)

    def mousePressEvent(self, event):
        self.active_tool.mouse_press(event)

    def mouseReleaseEvent(self, event):
        self.active_tool.mouse_release(event)

    def mouseMoveEvent(self, event):
        self.active_tool.mouse_move(event)

    def group_selection(self):
        try:
            print("--Start--")
            selected_items = self.scene.selectedItems()
            if not selected_items:
                return
            group = Group()
            self.scene.addItem(group)
            for item in selected_items:
                item.setSelected(False)
                group.addToGroup(item)
            group.setSelected(True)
            print("Group is created")
        except Exception as e:
            print (e)

    def ungroup_selection(self):
        selected_items = self.scene.selectedItems()

        for item in selected_items:
            if isinstance(item, Group):
                self.scene.destroyItemGroup(item)
                print("Group is ungrouped")