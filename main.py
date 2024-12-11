import os
import sys
from PyQt5.QtWidgets import QApplication, QFileDialog, QTableWidgetItem
from ui import ExcelProcessorUI
from sqlite_handler import SQLiteHandler
from excel_handler import ExcelHandler


class ExcelProcessorApp(ExcelProcessorUI):
    def __init__(self):
        super().__init__()
        self.import_button.clicked.connect(self.import_excel)
        self.execute_button.clicked.connect(self.execute_script)
        self.history_table.cellDoubleClicked.connect(self.export_history_to_excel)
        os.makedirs(self.history_folder, exist_ok=True)
        self.load_history()

    def load_history(self):
        """Load all SQLite files from the history folder."""
        self.history_table.setRowCount(0)
        for file_name in os.listdir(self.history_folder):
            if file_name.endswith(".db"):
                file_path = os.path.join(self.history_folder, file_name)
                row_position = self.history_table.rowCount()
                self.history_table.insertRow(row_position)
                self.history_table.setItem(row_position, 0, QTableWidgetItem(file_name))
                self.history_table.setItem(row_position, 1, QTableWidgetItem(file_path))

    def execute_script(self):
        """Run the user's custom script on the SQLite database."""
        file_path = QFileDialog.getOpenFileName(
            self, "Select SQLite Database", self.history_folder, "Database Files (*.db)"
        )[0]
        if file_path:
            script = self.code_editor.text()
            batch_size = 1  # Allow setting batch size if needed
            try:
                SQLiteHandler.execute_custom_script(file_path, script, batch_size)
                self.statusBar().showMessage("Script executed successfully.", 5000)
            except Exception as e:
                self.statusBar().showMessage(f"Error executing script: {e}", 5000)

    def import_excel(self):
        """Import an Excel file and save it to SQLite."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Excel File", "", "Excel Files (*.xlsx)"
        )
        if file_path:
            result_column = self.result_column_input.text() or "Result"
            try:
                excel_data = ExcelHandler.read_excel(file_path)
                db_name = os.path.basename(file_path).replace(".xlsx", ".db")
                db_path = os.path.join(self.history_folder, db_name)
                SQLiteHandler.save_excel_to_sqlite(excel_data, db_path, result_column)
                self.load_history()
                self.statusBar().showMessage(f"Imported and saved to {db_name}.", 5000)
            except Exception as e:
                self.statusBar().showMessage(f"Error importing Excel: {e}", 5000)

    def export_history_to_excel(self, row, column):
        """Export selected SQLite file to an Excel file."""
        file_path = self.history_table.item(row, 1).text()
        try:
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save Excel File", "", "Excel Files (*.xlsx)"
            )
            if save_path:
                SQLiteHandler.export_sqlite_to_excel(file_path, save_path)
                self.statusBar().showMessage(f"Exported to {save_path}.", 5000)
        except Exception as e:
            self.statusBar().showMessage(f"Error exporting to Excel: {e}", 5000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExcelProcessorApp()
    window.show()
    sys.exit(app.exec_())
