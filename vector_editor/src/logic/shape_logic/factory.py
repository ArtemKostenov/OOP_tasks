from src.logic.shape_logic.line import Line
from  src.logic.shape_logic.rect import Rectangle
from src.logic.shape_logic.ellipse import Ellipse
from src.logic.shape_logic.group import Group

class ShapeFactory:
    @staticmethod
    def create_shape(shape_type: str, start_point, end_point, color: str):
        x1, y1 = start_point.x(), start_point.y()
        x2, y2 = end_point.x(), end_point.y()

        if shape_type == "line":
            return Line(x1, y1, x2, y2, color)
        
        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)

        if shape_type == "rect":
            return Rectangle(x, y, w, h, color)
        elif shape_type == "ellipse":
            return Ellipse(x, y, w, h, color)
        else:
            raise ValueError(f"Unknown shape: {shape_type}")
        
    @staticmethod
    def from_dict(data: dict):
        shape_type = data.get("type")

        if shape_type == "group":
            return ShapeFactory._create_group(data)
        elif shape_type in ["line", "rect", "ellipse"]:
            return ShapeFactory._create_primitive(data)
        else:
            raise ValueError(f"Unknown type: {shape_type}")
        
    @staticmethod
    def _create_primitive(data: dict):
        props = data.get("props", {})
        shape_type = data.get("type")

        if shape_type == "rect":
            color = props.get("color", "black")
            obj = Rectangle(props['x'], props['y'], props['w'], props['h'], color)

        elif shape_type == "ellipse":
            color = props.get("color", "black") 
            obj = Ellipse(props['x'], props['y'], props['w'], props['h'], color)

        elif shape_type == "line":
            color = props.get("color", "black")
            obj = Line(props['x1'], props['y1'], props['x2'], props['y2'], color)

        if "pos" in data:
            obj.setPos(data["pos"][0], data["pos"][1])

        return obj
    
    @staticmethod
    def _create_group(data: dict):
        group = Group()

        x, y = data.get('pos', [0,0])
        group.setPos(x, y)

        children = data.get('children', [])
        for child in children:
            child = ShapeFactory.from_dict(child)

            group.addToGroup(child)

            if "pos" in child:
                cx, cy = child["pos"]
                child.setPos(cx, cy)

        return group