import pandas as pd


class ExcelHandler:
    @staticmethod
    def read_excel(file_path):
        """Read an Excel file into a Pandas DataFrame."""
        return pd.read_excel(file_path)
