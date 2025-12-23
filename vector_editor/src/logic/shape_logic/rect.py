from src.logic.shape_logic.shapes import Shape
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
            "pos": [self.x(), self.y()],
            "props": {
                "x": self.x, "y": self.y,
                "w": self.w, "h": self.h,
                "color": self.pen().color().name(),
                "stroke_width": self.pen().width()
            }
        }
    
    def set_geometry(self, start_point, end_point):
        self.x = min(start_point.x(), end_point.x())
        self.y = min(start_point.y(), end_point.y())
        self.w = abs(end_point.x() - start_point.x())
        self.h = abs(end_point.y() - start_point.y())

        path = QPainterPath()
        path.addRect(self.x, self.y, self.w, self.h)

        self.setPath(path)