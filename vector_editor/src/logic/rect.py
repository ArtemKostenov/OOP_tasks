from src.logic.shapes import Shape
from PySide6.QtGui import QPainterPath

class Rectangle(Shape):
    def __init__(self, x, y, w, h, color = "black", stroke_width = 2):
        super().__init__(color, stroke_width)

        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self._create_geometry()

    def _create_geometry(self):
        path = QPainterPath()
        path.addRect(self.x, self.y, self.w, self.h)

        self.setPath(path)

    @property
    def type_name(self) -> str:
        return "rect"
    
    def to_dict(self) -> dict:
        return {
            "type": self.type_name,
            "props": {
                "x": self.x, "y": self.y,
                "w": self.w, "h": self.h,
                "color": self.pen().color().name(),
                "stroke_width": self.pen().width()
            }
        }