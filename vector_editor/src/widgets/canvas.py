from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt, QPointF
from src.logic.factory import ShapeFactory

class EditorCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        self.setSceneRect(0, 0, 800, 600)
        self.setRenderHint(self.renderHints())
        self.setAlignment(Qt.AlignCenter)
        
        self.scene.setBackgroundBrush(Qt.white)

        self.active_tool = "line"
        self.current_color = "black"
        self.start_point = None

    def set_tool(self, tool_name):
        self.active_tool = tool_name

    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        x, y = scene_pos.x(), scene_pos.y()

        print(f"Клик на сцене {x:.1f}, {y:.1f} | Инструмент: {self.active_tool}")

        if event.button() == Qt.LeftButton:
            self.start_point = self.mapToScene(event.pos())
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            end_pont = self.mapToScene(event.pos())

            try:
                new_shape = ShapeFactory.create_shape(
                    self.active_tool,
                    self.start_point,
                    end_pont,
                    self.current_color
                )

                self.scene.addItem(new_shape)
                print(f"New shape: {self.active_tool}")
            except ValueError as e:
                print(e)
                pass
            finally:
                self.start_point = None
        
        super().mouseReleaseEvent(event)