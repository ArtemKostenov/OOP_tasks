from PySide6.QtWidgets import QMainWindow, QMessageBox, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QPushButton, QFileDialog
from PySide6.QtGui import QCloseEvent, QAction, QKeySequence
from src.widgets.canvas import EditorCanvas
from src.widgets.properties import PropertiesPanel
from src.logic.strategies import JsonSaveStrategy, ImageSaveStrategy
from src.logic.shape_logic.factory import ShapeFactory
from src.logic.io import FileManager
import json

class VectorEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        print("Окно создано")

        self.setWindowTitle("Vector Editor")
        self.resize(800, 600)

        self._init_ui()
        
    def _init_ui(self):
        self._setup_layout()
        self.statusBar().showMessage("Готов к работе") 

        menu = self.menuBar()
        file_menu = menu.addMenu("&File")

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Saving Project")
        save_action.triggered.connect(self.on_save_clicked)

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        save_action.setStatusTip("Opening Project")
        open_action.triggered.connect(self.on_open_clicked)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Close app")
        exit_action.triggered.connect(self.close)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(exit_action)

        tool = self.addToolBar("Main Toolbar")
        tool.addAction(exit_action)

        group_action = QAction("Group", self)
        group_action.setShortcut(QKeySequence("Ctrl+G"))
        group_action.triggered.connect(self.canvas.group_selection)

        ungroup_action = QAction("Ungroup", self)
        ungroup_action.setShortcut(QKeySequence("Ctrl+U"))
        ungroup_action.triggered.connect(self.canvas.ungroup_selection)
        
        stack = self.canvas.undo_stack

        undo_action = stack.createUndoAction(self, "&Undo")
        undo_action.setShortcut(QKeySequence.Undo)

        redo_action = stack.createRedoAction(self, "&Redo")
        redo_action.setShortcut(QKeySequence.Redo)

        delete_action = QAction("Delete", self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self.canvas.delete_selected)
        self.addAction(delete_action)

        edit_menu = self.menuBar().addMenu("&Edit")
        edit_menu.addAction(group_action)
        edit_menu.addAction(ungroup_action)
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addAction(delete_action)

    def closeEvent(self, event: QCloseEvent):
        print("Попытка закрыть окно")

        request = QMessageBox.question(self, "Attention", "Вы хотите выйти из приложения?", QMessageBox.Yes | QMessageBox.No)

        if request == QMessageBox.Yes:
            print("Окно закрыто")
            event.accept()
        else:
            print("Отмена")
            event.ignore()

    def _setup_layout(self):
        container = QWidget()
        self.setCentralWidget(container)

        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(0,0,0,0)

        tools_panel = QFrame()
        tools_panel.setFixedWidth(120)
        tools_panel.setStyleSheet("background-color: #555555;")

        tools_layout = QVBoxLayout(tools_panel)

        self.btn_select = QPushButton("Select")
        self.btn_line = QPushButton("Line")
        self.btn_rect = QPushButton("Rect")
        self.btn_ellipse = QPushButton("Ellipse")

        self.btn_select.setCheckable(True)
        self.btn_line.setCheckable(True)
        self.btn_rect.setCheckable(True)
        self.btn_ellipse.setCheckable(True)

        self.btn_select.setChecked(True)

        tools_layout.addWidget(self.btn_select)
        tools_layout.addWidget(self.btn_line)
        tools_layout.addWidget(self.btn_rect)
        tools_layout.addWidget(self.btn_ellipse)
        tools_layout.addStretch()

        self.btn_select.clicked.connect(lambda: self.on_change_tool("select"))
        self.btn_line.clicked.connect(lambda: self.on_change_tool("line"))
        self.btn_rect.clicked.connect(lambda: self.on_change_tool("rect"))
        self.btn_ellipse.clicked.connect(lambda: self.on_change_tool("ellipse"))

        self.current_tool = "select"

        self.canvas = EditorCanvas()
        self.canvas.scene.changed.connect(lambda: self.props_panel.on_selection_changed())

        main_layout.addWidget(tools_panel)
        main_layout.addWidget(self.canvas)
        
        self.props_panel = PropertiesPanel(self.canvas.scene, self.canvas.undo_stack)
        main_layout.addWidget(self.props_panel)

    def on_change_tool(self, tool_name):
        self.current_tool = tool_name
        print(f"Инструмент: {tool_name}")

        if tool_name == "line":
            self.btn_select.setChecked(False)
            self.btn_line.setChecked(True)
            self.btn_rect.setChecked(False)
            self.btn_ellipse.setChecked(False)
        elif tool_name == "rect":
            self.btn_select.setChecked(False)
            self.btn_line.setChecked(False)
            self.btn_rect.setChecked(True)
            self.btn_ellipse.setChecked(False)
        elif tool_name == "ellipse":
            self.btn_select.setChecked(False)
            self.btn_line.setChecked(False)
            self.btn_rect.setChecked(False)
            self.btn_ellipse.setChecked(True)
        else:
            self.btn_select.setChecked(True)
            self.btn_line.setChecked(False)
            self.btn_rect.setChecked(False)
            self.btn_ellipse.setChecked(False)

        self.canvas.set_tool(tool_name)
    
    def on_save_clicked(self):
        filters = "Vector Project (*.json);;PNG Image (*.png);;JPEG Image (*.jpg)"
        filename, selected_filter = QFileDialog.getSaveFileName(
            self, "Save File", "", filters
        )

        if not filename:
            return
        
        strategy = None

        if filename.lower().endswith(".png"):
            strategy = ImageSaveStrategy("PNG", background="transparent")
        elif filename.lower().endswith(".jpg"):
            strategy = ImageSaveStrategy("JPG", background="white")
        else:
            strategy = JsonSaveStrategy()

        try:
            strategy.save(filename, self.canvas.scene)
            self.statusBar().showMessage(f"Успешно сохранено в {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Не удалось сохранить файл:\n{str(e)}")

    def on_open_clicked(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Открыть проект", "", "Vector Project (*.json *.vec)"
        )

        if not path:
            return
        
        data = FileManager.load_project(path)

        self.canvas.scene.clear()
        self.canvas.undo_stack.clear()

        scene_info = data.get("scene", {})
        width = scene_info.get("width", 800)
        height = scene_info.get("height", 600)
        self.canvas.scene.setSceneRect(0, 0, width, height)

        shapes_data = data.get("shapes", [])

        errors_count = 0

        for shape in shapes_data:
            try:
                shape_obj = ShapeFactory.from_dict(shape)
                self.canvas.scene.addItem(shape_obj)
            except Exception as e:
                print(f"Ошибка загрузки фигуры: {e}")
                errors_count += 1

        if errors_count > 0:
            self.statusBar().showMessage(f"Загружено с ошибками ({errors_count} фигур пропущено)")
        else:
            self.statusBar().showMessage(f"Проект загруже: {path}")