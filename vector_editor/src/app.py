from PySide6.QtWidgets import QMainWindow, QMessageBox, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QPushButton
from PySide6.QtGui import QCloseEvent, QAction, QKeySequence
from src.widgets.canvas import EditorCanvas

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

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Close app")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        tool = self.addToolBar("Main Toolbar")
        tool.addAction(exit_action)

        group_action = QAction("Group", self)
        group_action.setShortcut(QKeySequence("Ctrl+G"))
        group_action.triggered.connect(self.canvas.group_selection)

        ungroup_action = QAction("Ungroup", self)
        ungroup_action.setShortcut(QKeySequence("Ctrl+U"))
        ungroup_action.triggered.connect(self.canvas.ungroup_selection)

        edit_menu = self.menuBar().addMenu("&Edit")
        edit_menu.addAction(group_action)
        edit_menu.addAction(ungroup_action)

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

        main_layout.addWidget(tools_panel)
        main_layout.addWidget(self.canvas)

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