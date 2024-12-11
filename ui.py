from code_editor import CodeEditor

from PyQt5.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QTableWidget,
    QVBoxLayout,
    QSplitter,
    QWidget,
    QPushButton,
    QLineEdit,
    QTableWidgetItem,
    QLabel,
    QTextEdit,
)
from PyQt5.QtCore import Qt


class ExcelProcessorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.history_folder = "./history"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Excel处理器")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # History Section
        history_layout = QVBoxLayout()
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(2)
        self.history_table.setHorizontalHeaderLabels(["File Name", "File Path"])
        history_layout.addWidget(QLabel("History (Double-click to export):"))
        history_layout.addWidget(self.history_table)

        # Import Section
        import_layout = QVBoxLayout()
        self.import_button = QPushButton("Import Excel")
        self.result_column_input = QLineEdit()
        self.result_column_input.setPlaceholderText("Result column name")
        import_layout.addWidget(self.result_column_input)
        import_layout.addWidget(self.import_button)

        # Code Editor Section
        editor_layout = QVBoxLayout()
        self.code_editor = CodeEditor()
        self.execute_button = QPushButton("Execute Script")
        self.stop_button = QPushButton("stop")
        editor_layout.addWidget(QLabel("Custom Python Script:"))
        editor_layout.addWidget(self.code_editor)
        editor_layout.addWidget(self.execute_button)
        editor_layout.addWidget(self.stop_button)

        # Combine Layouts
        layout.addLayout(history_layout)
        layout.addLayout(import_layout)
        layout.addLayout(editor_layout)

        # Set layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
