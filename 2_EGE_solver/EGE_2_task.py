from tkinter import * 
from tkinter import ttk
from tkinter import messagebox
from itertools import *

class Solver:
    def __init__(self):
        self.__task = None

    def __set_task(self, task):
        for c in task:
            if c not in '\u202f∨→≡∧¬xyzw() ':
                raise ValueError("Строка содержит недопустимые символы")
        self.__task = task.replace('\u202f', ' ').replace("∨", "or").replace("→", "<=").replace("≡", "==").replace("∧", "and").replace("¬", "1- ")       

    def make_table(self):
        result = []
        for x in 0,1:
            for y in 0,1:
                for z in 0,1:
                    for w in 0,1:
                       result.append(self.func_table(x, y, z, w))
        return(result)
    
    def func_table(self, x, y, z, w):
        return (x, y, z, w, int(eval(self.Task)))
    
    def func_solve(self, x, y, z, w):
        return(int(eval(self.Task)))
    
    def solve_task(self, values, holes):
        for r in product([0,1], repeat = holes):
            temp = 0
            current_values = [value[:] for value in values]
            for i in range(3):
                for j in range(5):
                    if current_values[i][j] == "":
                        current_values[i][j] = r[temp]
                        temp += 1
            tuple_values = tuple(tuple(x) for x in current_values)
            if len(tuple_values) == len(set(tuple_values)):
                for p in permutations('xyzw'):
                    if all(self.func_solve(**dict(zip(p,value))) == value[-1] for value in tuple_values):
                        return str(p)


    Task = property(lambda x: x.__task, __set_task)

class Buttons_widget(Frame):
    def __init__(self, parent):
        super().__init__(master = parent)

        Button(self, text="Построить таблицу истинности", font=("Arial", 14), command=lambda: self.btn_make_table_click()).pack(side=LEFT, padx=50)
        Button(self, text="Решить задание", font=("Arial", 14), command=lambda: self.btn_solve_task_click()).pack(side=RIGHT, padx=100)

        self.pack(fill=X, padx=10, pady=10)

    def btn_make_table_click():
        global entry
        if entry.get():
            try:
                global task
                task.Task = entry.get()
                show_table()
            except:
                messagebox.showerror("Ошибка ввода", "Введена некорректная функция")
        else:
            messagebox.showerror("Ошибка ввода", "Введите выражение из задания")
    
    def btn_solve_task_click():
        try:
            global task
            task_value, places = get_values()
            if task.Task == None:
                task.Task = entry.get()
            answer = task.solve_task(task_value, places)
            Label(matrix_panel, text=f"Ответ: {answer.replace("\'", '').replace(" ", '').replace("(", '').replace(")", '').replace(",", '')}", font=("Arial", 14, "bold")).pack()
        except:
            messagebox.showerror("Ошибка ввода","Проверьте введённые данные") 
    
clicks = 1
task = Solver()
current_tree = None
current_table_frame = None






def show_table():
    global current_tree, current_table_frame

    if current_table_frame:
        current_table_frame.destroy()

    current_table_frame = Frame(main_panel)
    current_table_frame.pack(side=LEFT, padx=20, pady=10, fill=BOTH, expand=True)
    
    Label(current_table_frame, text="Таблица истинности", font=("Arial", 12, "bold")).pack()
    
    columns = ("x", "y", "z", "w", "F")
    tree = ttk.Treeview(current_table_frame, columns=columns, show="headings", height=16)
    tree.pack(side=TOP, padx=10, pady=10, fill=BOTH, expand=True)

    tree.heading("x", text="X")
    tree.heading("y", text="Y")
    tree.heading("z", text="Z")
    tree.heading("w", text="W")
    tree.heading("F", text="F", command=lambda: _change_view())
    tree.column("#1", stretch=YES, width=80, anchor="c")
    tree.column("#2", stretch=YES, width=80, anchor="c")
    tree.column("#3", stretch=YES, width=80, anchor="c")
    tree.column("#4", stretch=YES, width=80, anchor="c")
    tree.column("#5", stretch=YES, width=80, anchor="c")

    global clicks

    for row in task.make_table():
        if clicks % 3 == 0:
            if row[4] == 0:
                tree.insert("", END, values=row)
        elif clicks % 2 == 0:
            if row[4] == 1:
                tree.insert("", END, values=row)
        else:
            tree.insert("", END, values=row)
    current_tree = tree

def _change_view():
    global clicks
    clicks += 1
    if clicks > 3:
        clicks = 1
    show_table()

def get_values():
    values = []
    holes = 0
    for i in range(3):
        row_values = []
        for j in range(5):
            value = entries[i][j].get()
            if value != "1" and value != "0" and value != "":
                raise ValueError("Неверный формат данных")
            if value == "":
                holes += 1
            if value == "1" or value == "0":
                row_values.append(int(value))
            else:
                row_values.append(value)
        values.append(row_values)
    return values, holes



root = Tk()
root.title("2 Task")
root.geometry("1000x610")

label_main = Label(text="Калькулятор задания 2 ЕГЭ", font=("Arial", 18))
label_main.pack()

label_input = Label(text="Введите выражение:", font=("Arial", 14), padx=10, pady=10)
label_input.pack()

entry = Entry(font=("Arial", 14), width=50)
entry.pack(anchor="center", padx=10, pady=5)


Buttons_widget(root)


main_panel = Frame(root)
main_panel.pack(fill=BOTH, expand=True, padx=10, pady=10)

matrix_panel = Frame(main_panel)
matrix_panel.pack(side=RIGHT, padx=20, pady=10, fill=Y)

Label(matrix_panel, text="Значения из задания", font=("Arial", 12, "bold")).pack()

matrix_grid_frame = Frame(matrix_panel)
matrix_grid_frame.pack(pady=10)

headers = ["x", "y", "z", "w", "F"]
for j, header in enumerate(headers):
    Label(matrix_grid_frame, text=header, font=("Arial", 10, "bold"), width=8).grid(row=0, column=j, padx=2, pady=2)

entries = []
for i in range(3):
    row_entries = []
    for j in range(5):
        entry_task = Entry(matrix_grid_frame, width=8, justify='center', font=("Arial", 10))
        entry_task.grid(row=i+1, column=j, padx=2, pady=2) 
        entry_task.insert(0, "") 
        row_entries.append(entry_task)
    entries.append(row_entries)

root.mainloop()