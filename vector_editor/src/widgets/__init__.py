from src.logic.rect import Rectangle
from src.logic.ellipse import Ellipse
from src.logic.line import Line

from PySide6.QtWidgets import QGraphicsView

class EditorCanvas(QGraphicsView):
    def __init__(self):
        # ... стандартный код ...
        
        # ТЕСТ: Добавляем фигуры вручную
        rect = Rectangle(50, 50, 100, 100, "red")
        line = Line(200, 50, 300, 150, "blue", 5)
        ellipse = Ellipse(50, 200, 150, 80, "green")
        
        self.scene.addItem(rect)
        self.scene.addItem(line)
        self.scene.addItem(ellipse)