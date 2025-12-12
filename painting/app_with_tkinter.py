from tkinter import *

class Shape:
    def __init__(self):
        self.__name = "Shape"
        self.__type = None
        self.__color = "white"
        self.__width = 5

        if not hasattr(self, "draw_figure"):
            raise NotImplementedError("You can`t make this object!")
        
    def __set_name(self, name):
        self.__name = name

    def __set_type(self, type):
        self.__type = type
    
    def __set_color(self, color):
        self.__color = color

    def __set_width(self, width):
        self.__width = width

    def draw_figure(self):
        pass

    Name = property(lambda x: x.__name, __set_name)
    Type = property(lambda x: x.__type, __set_type)
    Color = property(lambda x: x.__color, __set_color)
    Width = property(lambda x: x.__width, __set_width)

class Point:
    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    def __set_x(self, x):
        self.__x = x

    def __set_y(self, y):
        self.__y = y

    X = property(lambda x: x.__x, __set_x)
    Y = property(lambda x: x.__y, __set_y)


class Line(Shape):
    def __init__(self, start, end):
        super().__init__()
        self.__type = "Line"
        self.__name = "Default Line"
        self.__start = start
        self.__end = end

    def __set_start(self, start):
        self.__start = start
    
    def __set_end(self, end):
        self.__end = end
    
    def draw_figure(self, canvas):
        x_0, y_0 = self.__start.X, self.__start.Y
        x_1, y_1 = self.__end.X, self.__end.Y
        canvas.create_line(x_0, y_0, x_1, y_1, width = self.Width, fill = self.Color)

    Start = property(lambda x: x.__start, __set_start)
    End = property(lambda x: x.__end, __set_end)


class Rectangle(Shape):
    def __init__(self, start, end):
        super().__init__()
        self.__type = "Rectangle"
        self.__name = "Default Rectangle"
        self.__start = start
        self.__end = end

    def __set_start(self, start):
        self.__start = start
    
    def __set_end(self, end):
        self.__end = end
    
    def draw_figure(self, canvas):
        x_0, y_0 = self.__start.X, self.__start.Y
        x_1, y_1 = self.__end.X, self.__end.Y
        canvas.create_rectangle(x_0, y_0, x_1, y_1, width = self.Width, fill = self.Color)

    Start = property(lambda x: x.__start, __set_start)
    End = property(lambda x: x.__end, __set_end)

root = Tk()
root.title("App with Tkinter")
root.geometry("400x400")


canvas = Canvas(bg="white", width=300, height=300)
canvas.pack(anchor=CENTER, expand=1)

line = Line(Point(10, 10), Point(100, 100))
line.Color = "Red"
line.draw_figure(canvas)

rec = Rectangle(Point(100, 200), Point(200, 100))
rec.Color = "Green"
rec.draw_figure(canvas)

root.mainloop()