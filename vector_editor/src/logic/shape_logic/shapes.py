from abc import ABC, abstractmethod
from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtGui import QPen, QColor
from PySide6.QtCore import QPointF

class Shape(QGraphicsPathItem):
    def __init__(self, color: str = "black", stroke_width: int = 2):
        super().__init__()

        self.color = color
        self.stroke_width = stroke_width

        self._setup_pen()
        self._setup_flags()

    def _setup_pen(self):
        pen = QPen(QColor(self.color))
        pen.setWidth(self.stroke_width)
        self.setPen(pen)

    def _setup_flags(self):
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemSendsGeometryChanges)

    def set_stroke_width(self, width: int):
        pen = self.pen()
        pen.setWidth(width)
        self.setPen(pen)

    @property
    @abstractmethod
    def type_name(self) -> str:
        pass
    @abstractmethod
    def to_dict(self) -> dict:
        pass
    @abstractmethod
    def set_geometry(self, start_point: QPointF, end_point: QPointF):
        pass

    def set_active_color(self, color: str):
        self.color = color
        self._setup_pen()
