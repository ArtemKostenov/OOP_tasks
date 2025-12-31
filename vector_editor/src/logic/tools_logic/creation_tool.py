from src.logic.shape_logic.factory import ShapeFactory
from src.logic.tools_logic.tools import Tool
from src.logic.commands.commands import AddShapeCommand
from PySide6.QtCore import Qt

class CreationTool(Tool):
    def __init__(self, canvas_view, shape_type: str, undo_stack, color: str = "black"):
        super().__init__(canvas_view)
        self.shape_type = shape_type
        self.undo_stack = undo_stack
        self.color = color
        self.start_pos = None
        self.temp_shape = None

    def mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = self.view.mapToScene(event.pos())

            try:
                self.temp_shape = ShapeFactory.create_shape(
                    self.shape_type,
                    self.start_pos,
                    self.start_pos,
                    self.color
                )
                self.scene.addItem(self.temp_shape)
            except ValueError as e:
                print(e)

    def mouse_move(self, event):
        if self.temp_shape and self.start_pos:
            current_pos = self.view.mapToScene(event.pos())
            self.temp_shape.set_geometry(self.start_pos, current_pos)

    def mouse_release(self, event):
        if self.temp_shape:
            self.scene.removeItem(self.temp_shape)
            self.temp_shape = None

            end_pos = self.view.mapToScene(event.pos())
            try:
                final_shape = ShapeFactory.create_shape(
                    self.shape_type, self.start_pos, end_pos, "black"
                )

                command = AddShapeCommand(self.scene, final_shape)
                self.undo_stack.push(command)

                print(f"Command pushed: {command.text()}")
            except ValueError as e:
                print("daun)")
                print(e)

        '''
        if event.button() == Qt.LeftButton:
            self.start_pos = None
            self.temp_shape = None
        '''