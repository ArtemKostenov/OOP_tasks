import math

class Shape:
    def __init__(self):
        self._name = "Figure"
    @property
    def __get_perimeter():
        pass
    def GetSquare():
        pass

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        self._name = name    

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Circle(Shape):
    def __init__(self, point, radius):
        super().__init__()

        if radius <= 0:
            raise TypeError("Wrong radius!")

        self.center = point
        self.radius = radius
    def GetSquare(self):
        return self.radius**2 * math.pi
    def GetPerimeter(self):
        return self.radius * 2 * math.pi
    
class Triangle(Shape):
    def __init__(self, points):
        super().__init__()

        if len(points) != 3:
            raise TypeError("Not enough points or too many!")
        self.points = points

        sides = self.GetSides()
        if (sides[0] >= sides[1] + sides[2]) or (sides[1] >= sides[0] + sides[2]) or (sides[2] >= sides[0] + sides[1]):
            raise TypeError("This triangle not exist!")

    def GetSides(self):
        a = math.sqrt((self.points[0].x-self.points[1].x)**2 + (self.points[0].y - self.points[1].y)**2)
        b = math.sqrt((self.points[0].x-self.points[2].x)**2 + (self.points[0].y - self.points[2].y)**2)
        c = math.sqrt((self.points[2].x-self.points[1].x)**2 + (self.points[2].y - self.points[1].y)**2)

        return [a,b,c]
    def GetPerimeter(self):
        sides = self.GetSides()
        return sides[0]+sides[1]+sides[2]
    
    def GetSquare(self):
        param = self.GetPerimeter()/2
        sides = self.GetSides()
        return math.sqrt(param*(param-sides[0])*(param-sides[1])*(param-sides[2]))
    
class Rectangle(Shape):
    def __init__(self, points): #точки должны идти по очереди(после предыдущей не может быть точки по диагонали)
        super().__init__()

        if len(points) != 4:
            raise TypeError("Not enough points or too many!")
        self.points = points

    def GetSides(self):
        a = math.sqrt((self.points[0].x-self.points[1].x)**2 + (self.points[0].y - self.points[1].y)**2)
        b = math.sqrt((self.points[0].x-self.points[2].x)**2 + (self.points[0].y - self.points[2].y)**2)
        c = math.sqrt((self.points[1].x-self.points[3].x)**2 + (self.points[1].y - self.points[3].y)**2)
        d = math.sqrt((self.points[2].x-self.points[3].x)**2 + (self.points[2].y - self.points[3].y)**2)
        
        return [a,b,c,d]
    def GetPerimeter(self):
        sides = self.GetSides()
        return 2*(sides[0]+sides[1])
    def GetSquare(self):
        sides = self.GetSides()
        return sides[0]*sides[1]

'''
myTriangle = Triangle([Point(0, 0), Point(0,4), Point(2, 2)])
myRectangle = Rectangle([Point(0,0), Point(3,0), Point(0,3), Point(3,3)])
print(myTriangle.GetSquare())
print(myTriangle.GetPerimeter())
print(myTriangle.name)
myTriangle.name = "Triangle"
print(myTriangle.name)
print(myRectangle.GetPerimeter())
print(myRectangle.GetSquare())
'''