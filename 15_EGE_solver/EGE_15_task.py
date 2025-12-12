import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, QHeaderView)
from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from PySide6.QtCore import Qt, QRectF

class Interval:
    def __init__(self, name, start, end):
        self.name = name
        self.start = float(start)
        self.end = float(end)

    def __contains__(self, item):
        return self.start <= item <= self.end

    def __repr__(self):
        return f"{self.name}: [{self.start}, {self.end}]"


class LogicSolver:
    def __init__(self, expression, intervals, search_range=(0, 100), step=0.5):
        self.expression = expression
        self.intervals = {i.name: i for i in intervals} 
        self.search_range = search_range
        self.step = step

    def check_expression(self, x, a_val_bool):
        context = {}
        for name, interval in self.intervals.items():
            context[name] = interval
        if a_val_bool:
            context['A'] = [x]
        else:
            context['A'] = []
        
        context['x'] = x

        try:
            return bool(eval(self.expression, {}, context))
        except Exception as e:
            raise ValueError(f"Ошибка в формуле: {e}")

    def solve(self, mode="min", target_value=True):
        points_in_a = []
        current = self.search_range[0]
        
        while current <= self.search_range[1]:
            res_without_a = self.check_expression(current, False)
            res_with_a = self.check_expression(current, True)
            
            if mode == "min":
                if res_without_a != target_value:
                    points_in_a.append(current)
            
            elif mode == "max":
                if res_with_a == target_value:
                    points_in_a.append(current)

            current += self.step
            current = round(current, 1)

        if not points_in_a:
            return None
        
        return Interval("A (Result)", min(points_in_a), max(points_in_a))

class IntervalChart(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(300)
        self.intervals = []
        self.result_interval = None
        self.bg_color = QColor(240, 240, 240)

    def update_data(self, intervals, result):
        self.intervals = intervals
        self.result_interval = result
        self.update() 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), self.bg_color)

        w = self.width()
        h = self.height()
        margin = 40
        axis_y = h - 50

        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawLine(margin, axis_y, w - margin, axis_y)

        all_vals = [0, 50]
        for i in self.intervals:
            all_vals.extend([i.start, i.end])
        if self.result_interval:
            all_vals.extend([self.result_interval.start, self.result_interval.end])
        
        min_val = min(all_vals)
        max_val = max(all_vals)
        if max_val == min_val: max_val += 10
        scale_len = max_val - min_val
        if scale_len == 0: scale_len = 10
        
        px_per_unit = (w - 2 * margin) / scale_len

        def val_to_x(val):
            return margin + (val - min_val) * px_per_unit

        step_grid = 10 if scale_len > 50 else 5
        if scale_len < 20: step_grid = 1
        
        current_grid = int(min_val)
        while current_grid <= int(max_val) + 1:
            x_pos = val_to_x(current_grid)
            if margin <= x_pos <= w - margin:
                painter.drawLine(int(x_pos), axis_y - 5, int(x_pos), axis_y + 5)
                painter.drawText(int(x_pos) - 10, axis_y + 20, str(current_grid))
            current_grid += step_grid

        def draw_interval_bar(interval, y_pos, color_code, is_result=False):
            x1 = val_to_x(interval.start)
            x2 = val_to_x(interval.end)
            
            if x2 < margin or x1 > w - margin: return
            x1 = max(x1, margin)
            x2 = min(x2, w - margin)
            
            width_bar = x2 - x1
            height_bar = 20
            rect = QRectF(x1, y_pos, width_bar, height_bar)
            
            color = QColor(color_code)
            color.setAlpha(150 if not is_result else 200)
            painter.setBrush(QBrush(color))
            
            pen = QPen(Qt.GlobalColor.black, 1)
            if is_result:
                pen = QPen(Qt.GlobalColor.red, 2)
            painter.setPen(pen)
            
            painter.drawRect(rect)
            label = f"{interval.name} [{interval.start}, {interval.end}]"
            painter.drawText(int(x1), int(y_pos) - 5, label)

        y_offset = axis_y - 40
        colors = [Qt.GlobalColor.blue, Qt.GlobalColor.green, Qt.GlobalColor.cyan, Qt.GlobalColor.magenta]
        
        for idx, interval in enumerate(self.intervals):
            c = colors[idx % len(colors)]
            draw_interval_bar(interval, y_offset, c)
            y_offset -= 35

        if self.result_interval:
            draw_interval_bar(self.result_interval, y_offset - 20, Qt.GlobalColor.red, is_result=True)
        else:
            painter.drawText(margin, 30, "Результат: нет подходящих точек")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logic Interval Solver")
        self.resize(950, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Выражение:"))
        self.formula_input = QLineEdit()
        self.formula_input.setText("") 
        top_layout.addWidget(self.formula_input)
        main_layout.addLayout(top_layout)
        
        help_label = QLabel("Синтаксис: (x in P), and, or, not, <= (импликация), == (равенство).")
        help_label.setStyleSheet("color: gray; font-size: 11px;")
        main_layout.addWidget(help_label)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Имя", "Начало", "Конец"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setRowCount(0)
        main_layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить отрезок")
        add_btn.clicked.connect(lambda: self.add_interval_row("Q", 0, 10))
        del_btn = QPushButton("Удалить")
        del_btn.clicked.connect(self.remove_row)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        main_layout.addLayout(btn_layout)

        settings_box = QWidget()
        settings_box.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; padding: 5px;")
        settings_layout = QHBoxLayout(settings_box)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Найти минимальный A", "Найти максимальный A"])
        settings_layout.addWidget(QLabel("Искать:"))
        settings_layout.addWidget(self.mode_combo)

        self.target_combo = QComboBox()
        self.target_combo.addItems(["Тождественно истинно (1)", "Тождественно ложно (0)"])
        settings_layout.addWidget(QLabel("Значение выражения:"))
        settings_layout.addWidget(self.target_combo)
        
        calc_btn = QPushButton("ВЫЧИСЛИТЬ")
        calc_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; border: none; padding: 5px 15px;")
        calc_btn.clicked.connect(self.run_calculation)
        settings_layout.addWidget(calc_btn)
        
        main_layout.addWidget(settings_box)

        self.chart = IntervalChart()
        main_layout.addWidget(self.chart)

        self.result_label = QLabel("Ожидание...")
        self.result_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        main_layout.addWidget(self.result_label)

    def add_interval_row(self, name, start, end):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))
        self.table.setItem(row, 1, QTableWidgetItem(str(start)))
        self.table.setItem(row, 2, QTableWidgetItem(str(end)))

    def remove_row(self):
        row = self.table.currentRow()
        if row >= 0: self.table.removeRow(row)

    def get_intervals_from_ui(self):
        intervals = []
        try:
            for row in range(self.table.rowCount()):
                name = self.table.item(row, 0).text().strip()
                start = float(self.table.item(row, 1).text())
                end = float(self.table.item(row, 2).text())
                if name:
                    intervals.append(Interval(name, start, end))
            return intervals
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Проверьте числа в таблице")
            return None

    def run_calculation(self):
        intervals = self.get_intervals_from_ui()
        if not intervals: return

        formula = self.formula_input.text()
        
        mode = "min" if self.mode_combo.currentIndex() == 0 else "max"
        
        target_is_true = (self.target_combo.currentIndex() == 0)

        all_coords = [i.end for i in intervals]
        max_search = max(all_coords) + 30 if all_coords else 100
        
        solver = LogicSolver(formula, intervals, search_range=(0, max_search))
        
        try:
            result_a = solver.solve(mode=mode, target_value=target_is_true)
            
            self.chart.update_data(intervals, result_a)
            
            target_text = "1" if target_is_true else "0"
            if result_a:
                self.result_label.setText(f"Чтобы выражение = {target_text}, {mode} отрезок A: [{result_a.start}, {result_a.end}]")
            else:
                self.result_label.setText(f"Для выражения = {target_text} решение не найдено (пустое множество)")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())