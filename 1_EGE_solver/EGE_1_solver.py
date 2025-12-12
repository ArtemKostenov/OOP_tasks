import sys
import json
from itertools import permutations
from typing import Optional, List, Dict, Set

from PySide6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene,
                               QGraphicsItem, QGraphicsEllipseItem,
                               QGraphicsLineItem, QGraphicsTextItem,
                               QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QPushButton, QFileDialog, QMessageBox, QLabel, QScrollArea)
from PySide6.QtCore import Qt, QRectF, QLineF, QPointF, Signal, QObject
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QPainterPathStroker, QAction


# ==========================================
# 1. Configuration (Конфигурация)
# ==========================================
class GraphConfig:
    NODE_DIAMETER = 30
    NODE_RADIUS = NODE_DIAMETER / 2
    EDGE_WIDTH = 2
    MIN_DISTANCE = 40

    COLOR_BG = QColor(40, 40, 40)
    COLOR_NODE = QColor(0, 255, 255)
    COLOR_NODE_ACTIVE = QColor(255, 0, 255)
    COLOR_EDGE = QColor(255, 255, 255)
    COLOR_TEXT = QColor(255, 255, 255)

    TABLE_BG = QColor(50, 50, 50)
    TABLE_TEXT = QColor(255, 255, 255)
    TABLE_DIAGONAL = QColor(80, 80, 80)


# ==========================================
# 2. Graph Visual Entities (Виджеты Графа)
# ==========================================
class EdgeItem(QGraphicsLineItem):
    def __init__(self, source_item, dest_item):
        super().__init__()
        self.source = source_item
        self.dest = dest_item
        self.setPen(QPen(GraphConfig.COLOR_EDGE, GraphConfig.EDGE_WIDTH))
        self.setZValue(0)
        self.update_geometry()

    def update_geometry(self):
        line = QLineF(self.source.scenePos(), self.dest.scenePos())
        self.setLine(line)

    def shape(self):
        path = super().shape()
        stroker = QPainterPathStroker()
        stroker.setWidth(10)
        return stroker.createStroke(path)


class NodeItem(QGraphicsEllipseItem):
    def __init__(self, name: str, x: float, y: float):
        rect = QRectF(-GraphConfig.NODE_RADIUS, -GraphConfig.NODE_RADIUS,
                      GraphConfig.NODE_DIAMETER, GraphConfig.NODE_DIAMETER)
        super().__init__(rect)
        self.name = name
        self.edges: List[EdgeItem] = []
        self.setBrush(QBrush(GraphConfig.COLOR_NODE))
        self.setPen(QPen(Qt.NoPen))
        self.setPos(x, y)
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self._create_label(name)

    def _create_label(self, text: str):
        self.label = QGraphicsTextItem(text, self)
        self.label.setDefaultTextColor(GraphConfig.COLOR_TEXT)
        font = self.label.font()
        font.setBold(True)
        self.label.setFont(font)
        # Центрируем текст
        rect = self.label.boundingRect()
        self.label.setPos(-rect.width() / 2, -rect.height() / 2)

    def set_highlighted(self, is_active: bool):
        color = GraphConfig.COLOR_NODE_ACTIVE if is_active else GraphConfig.COLOR_NODE
        self.setBrush(QBrush(color))

    def add_connection(self, edge: EdgeItem):
        self.edges.append(edge)

    def remove_connection(self, edge: EdgeItem):
        if edge in self.edges:
            self.edges.remove(edge)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            for edge in self.edges:
                edge.update_geometry()
        return super().itemChange(change, value)


# ==========================================
# 3. Graph Logic Managers
# ==========================================
class ChainBuilder:
    def __init__(self):
        self.active_node: Optional[NodeItem] = None

    def start_or_continue(self, node: NodeItem) -> Optional[NodeItem]:
        prev_node = self.active_node
        if self.active_node:
            self.active_node.set_highlighted(False)
        self.active_node = node
        self.active_node.set_highlighted(True)
        return prev_node

    def reset(self):
        if self.active_node:
            self.active_node.set_highlighted(False)
            self.active_node = None


class GraphManager(QObject):
    node_count_changed = Signal(int)

    def __init__(self, scene: QGraphicsScene):
        super().__init__()
        self.scene = scene
        self.node_counter = 0

    def reset(self):
        self.node_counter = 0
        self.scene.clear()
        self.node_count_changed.emit(0)

    def generate_name(self) -> str:
        n = self.node_counter
        name = ""
        while n >= 0:
            name = chr(ord('A') + (n % 26)) + name
            n = n // 26 - 1
        self.node_counter += 1
        return name

    def create_node(self, pos: QPointF, name: str = None) -> NodeItem:
        if name is None:
            name = self.generate_name()
        else:
            self.node_counter += 1

        node = NodeItem(name, pos.x(), pos.y())
        self.scene.addItem(node)
        self.node_count_changed.emit(self.get_node_count())
        return node

    def create_edge(self, u: NodeItem, v: NodeItem):
        if u == v: return
        for edge in u.edges:
            if (edge.source == u and edge.dest == v) or (edge.source == v and edge.dest == u):
                return
        edge = EdgeItem(u, v)
        self.scene.addItem(edge)
        u.add_connection(edge)
        v.add_connection(edge)

    def delete_item(self, item: QGraphicsItem):
        if isinstance(item, NodeItem):
            for edge in list(item.edges):
                self.delete_item(edge)
            self.scene.removeItem(item)
            self.node_count_changed.emit(self.get_node_count())
        elif isinstance(item, EdgeItem):
            item.source.remove_connection(item)
            item.dest.remove_connection(item)
            self.scene.removeItem(item)

    def get_node_count(self) -> int:
        return sum(1 for item in self.scene.items() if isinstance(item, NodeItem))

    def is_position_valid(self, pos: QPointF) -> bool:
        for item in self.scene.items():
            if isinstance(item, NodeItem):
                distance = QLineF(pos, item.scenePos()).length()
                if distance < GraphConfig.MIN_DISTANCE:
                    return False
        return True

    def get_graph_structure(self) -> Dict[str, Set[str]]:
        structure = {}
        nodes = [item for item in self.scene.items() if isinstance(item, NodeItem)]
        for node in nodes:
            structure[node.name] = set()

        for node in nodes:
            for edge in node.edges:
                other = edge.dest if edge.source == node else edge.source
                structure[node.name].add(other.name)
        
        return structure


# ==========================================
# 4. Matrix Widget (Таблица весов)
# ==========================================
class WeightMatrixWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(0)
        self.setRowCount(0)
        self.setWindowTitle("Матрица весов")

        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {GraphConfig.TABLE_BG.name()};
                color: {GraphConfig.TABLE_TEXT.name()};
                gridline-color: #666;
            }}
            QHeaderView::section {{
                background-color: #333;
                color: white;
                padding: 4px;
                border: 1px solid #666;
            }}
            QLineEdit {{ color: white; background-color: #444; }}
        """)

        self.itemChanged.connect(self.on_item_changed)
        self.horizontalHeader().setDefaultSectionSize(40)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

    def update_size(self, node_count: int):
        self.setRowCount(node_count)
        self.setColumnCount(node_count)

        headers = [str(i + 1) for i in range(node_count)]
        self.setHorizontalHeaderLabels(headers)
        self.setVerticalHeaderLabels(headers)

        self.blockSignals(True)
        for r in range(node_count):
            for c in range(node_count):
                item = self.item(r, c)
                if not item:
                    item = QTableWidgetItem("")
                    item.setTextAlignment(Qt.AlignCenter)
                    self.setItem(r, c, item)

                if r == c:
                    item.setFlags(Qt.ItemIsEnabled)
                    item.setBackground(QBrush(GraphConfig.TABLE_DIAGONAL))
                else:
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
                    item.setBackground(QBrush(GraphConfig.TABLE_BG))
        self.blockSignals(False)

    def on_item_changed(self, item):
        row = item.row()
        col = item.column()
        if row == col: return

        text = item.text()
        self.blockSignals(True)
        symmetric_item = self.item(col, row)
        if symmetric_item:
            symmetric_item.setText(text)
        self.blockSignals(False)

    def get_data(self) -> List[List[str]]:
        rows = self.rowCount()
        data = []
        for r in range(rows):
            row_data = []
            for c in range(rows):
                item = self.item(r, c)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data

    def set_data(self, data: List[List[str]]):
        size = len(data)
        self.update_size(size)
        self.blockSignals(True)
        for r in range(size):
            for c in range(size):
                if r < len(data) and c < len(data[r]):
                    val = data[r][c]
                    item = self.item(r, c)
                    if item:
                        item.setText(val)
        self.blockSignals(False)

    def get_structure(self) -> Dict[str, Set[str]]:
        structure = {}
        rows = self.rowCount()
        headers = [str(i + 1) for i in range(rows)]
        
        for r in range(rows):
            node_idx = headers[r]
            neighbors = set()
            for c in range(rows):
                if r == c: continue
                item = self.item(r, c)
                if item and item.text().strip() and item.text().strip() != '0':
                    neighbors.add(headers[c])
            structure[node_idx] = neighbors
        
        return structure


# ==========================================
# 5. Graph Scene
# ==========================================
class GraphScene(QGraphicsScene):
    def __init__(self, manager: GraphManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.chain_builder = ChainBuilder()
        self.setBackgroundBrush(QBrush(GraphConfig.COLOR_BG))
        self.setSceneRect(0, 0, 800, 600)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Shift:
            self.chain_builder.reset()
        super().keyReleaseEvent(event)

    def mousePressEvent(self, event):
        pos = event.scenePos()
        item = self.itemAt(pos, self.views()[0].transform())

        if event.button() == Qt.LeftButton:
            # Режим создания связей (Shift + Click)
            if event.modifiers() & Qt.ShiftModifier:
                if isinstance(item, NodeItem):
                    prev_node = self.chain_builder.start_or_continue(item)
                    if prev_node:
                        self.manager.create_edge(prev_node, item)
                    event.accept()
                    return
                else:
                    self.chain_builder.reset()
            else:
                self.chain_builder.reset()

            # Создание узла
            if item is None:
                if self.manager.is_position_valid(pos):
                    self.manager.create_node(pos)
                event.accept()
                return

            super().mousePressEvent(event)

        elif event.button() == Qt.RightButton:
            # Удаление
            self.chain_builder.reset()
            if item:
                self.manager.delete_item(item)
                event.accept()


class GraphSolver:
    @staticmethod
    def solve(graph_structure: Dict[str, Set[str]], matrix_structure: Dict[str, Set[str]]) -> List[Dict[str, str]]:
        graph_nodes = sorted(list(graph_structure.keys()))
        table_nodes = sorted(list(matrix_structure.keys())) # ['1', '2', '3'...]
        
        n = len(graph_nodes)
        m = len(table_nodes)
        
        if n == 0 or m == 0:
            return []
        
        if n != m:
            return []

        solutions = []

        for p in permutations(graph_nodes):
            mapping = {t_node: g_node for t_node, g_node in zip(table_nodes, p)}
            transformed_matrix = {}

            for t_node, neighbors in matrix_structure.items():
                mapped_node = mapping[t_node]
                mapped_neighbors = {mapping[n] for n in neighbors}
                transformed_matrix[mapped_node] = mapped_neighbors
            
            if transformed_matrix == graph_structure:
                solutions.append(mapping)

        return solutions


# ==========================================
# 7. Main Application Window
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тренажер Задания №1 ЕГЭ (Informatics Solver)")
        self.resize(1200, 700)

        # 1. Инициализация
        self.scene_dummy = QGraphicsScene()
        self.graph_manager = GraphManager(self.scene_dummy)
        self.scene = GraphScene(self.graph_manager, self)
        self.graph_manager.scene = self.scene

        # 2. Виджеты
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)

        self.matrix_widget = WeightMatrixWidget()
        
        self.solve_button = QPushButton("Найти соответствие (Решить)")
        self.solve_button.setStyleSheet("background-color: #2A82DA; color: white; font-weight: bold; padding: 10px;")
        self.solve_button.clicked.connect(self.solve_graph)
        
        self.result_label = QLabel("Нарисуйте граф справа, заполните веса слева и нажмите 'Решить'")
        self.result_label.setStyleSheet("color: white; background-color: #222; padding: 10px; border: 1px solid #444;")
        self.result_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.result_label.setWordWrap(True)
        
        # Скролл для результатов, если их много
        scroll = QScrollArea()
        scroll.setWidget(self.result_label)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: #222; border: none;")

        # 3. Связи
        self.graph_manager.node_count_changed.connect(self.matrix_widget.update_size)

        # 4. Лейауты
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("<b>1. Матрица весов</b> (введите любые числа, где есть связь)"))
        left_layout.addWidget(self.matrix_widget)
        left_layout.addWidget(self.solve_button)
        left_layout.addWidget(QLabel("<b>Результат решения:</b>"))
        left_layout.addWidget(scroll)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(QLabel("<b>2. Граф</b> (ЛКМ: узел, Shift+ЛКМ: связь, ПКМ: удалить)"))
        right_layout.addWidget(self.view)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)

        self.setCentralWidget(central_widget)
        self.create_menu()

    def create_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("Файл")

        save_action = QAction("Сохранить упражнение...", self)
        save_action.triggered.connect(self.save_exercise)
        file_menu.addAction(save_action)

        load_action = QAction("Загрузить упражнение...", self)
        load_action.triggered.connect(self.load_exercise)
        file_menu.addAction(load_action)

        clear_action = QAction("Очистить всё", self)
        clear_action.triggered.connect(self.clear_all)
        file_menu.addAction(clear_action)

    def solve_graph(self):
        graph_struct = self.graph_manager.get_graph_structure() 
        matrix_struct = self.matrix_widget.get_structure()

        if not graph_struct:
            QMessageBox.warning(self, "Пусто", "Граф пуст.")
            return
        
        solutions = GraphSolver.solve(graph_struct, matrix_struct)

        if not solutions:
            self.result_label.setText(
                "Решений не найдено.\n\n"
                "Возможные причины:\n"
                "1. Структура графа не совпадает с отмеченными связями в таблице.\n"
                "2. Разное количество вершин."
            )
        else:
            text = f"Найдено решений: {len(solutions)}\n"
            text += "-" * 30 + "\n"
            
            for i, sol in enumerate(solutions):
                text += f"Решение #{i+1}:\n"
                sorted_items = sorted(sol.items(), key=lambda x: int(x[0]))
                row_str = []
                for num, letter in sorted_items:
                    row_str.append(f"{num}➜{letter}")
                text += "  ".join(row_str) + "\n\n"
            
            self.result_label.setText(text)

    def clear_all(self):
        self.graph_manager.reset()
        self.matrix_widget.update_size(0)
        self.result_label.setText("")

    def save_exercise(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить", "", "JSON (*.json)")
        if not file_path: return

        nodes_data = []
        node_id_map = {}
        items = [i for i in self.scene.items() if isinstance(i, NodeItem)]
        items.sort(key=lambda x: x.name)
        
        for idx, node in enumerate(items):
            node_id_map[node] = idx
            nodes_data.append({
                "id": idx, "name": node.name,
                "x": node.pos().x(), "y": node.pos().y()
            })

        edges_data = []
        processed = set()
        for node in items:
            for edge in node.edges:
                if edge not in processed:
                    processed.add(edge)
                    u = node_id_map.get(edge.source)
                    v = node_id_map.get(edge.dest)
                    if u is not None and v is not None:
                        edges_data.append({"u": u, "v": v})

        data = {
            "graph": {"nodes": nodes_data, "edges": edges_data, "counter": self.graph_manager.node_counter},
            "matrix": self.matrix_widget.get_data()
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def load_exercise(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть", "", "JSON (*.json)")
        if not file_path: return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.clear_all()
            
            g_data = data.get("graph", {})
            self.graph_manager.node_counter = g_data.get("counter", 0)
            
            id_map = {}
            for n in g_data.get("nodes", []):
                node = self.graph_manager.create_node(QPointF(n["x"], n["y"]), n["name"])
                id_map[n["id"]] = node
                
            for e in g_data.get("edges", []):
                u, v = id_map.get(e["u"]), id_map.get(e["v"])
                if u and v: self.graph_manager.create_edge(u, v)
            
            self.matrix_widget.set_data(data.get("matrix", []))
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Темная тема
    p = app.palette()
    p.setColor(p.ColorRole.Window, QColor(53, 53, 53))
    p.setColor(p.ColorRole.WindowText, Qt.white)
    p.setColor(p.ColorRole.Base, QColor(35, 35, 35))
    p.setColor(p.ColorRole.AlternateBase, QColor(53, 53, 53))
    p.setColor(p.ColorRole.ToolTipBase, Qt.white)
    p.setColor(p.ColorRole.ToolTipText, Qt.white)
    p.setColor(p.ColorRole.Text, Qt.white)
    p.setColor(p.ColorRole.Button, QColor(53, 53, 53))
    p.setColor(p.ColorRole.ButtonText, Qt.white)
    p.setColor(p.ColorRole.Highlight, QColor(42, 130, 218))
    p.setColor(p.ColorRole.HighlightedText, Qt.black)
    app.setPalette(p)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())