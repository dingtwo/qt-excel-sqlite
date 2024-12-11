import sqlite3


class SQLiteHandler:
    @staticmethod
    def save_excel_to_sqlite(excel_data, db_path, result_column):
        """Save Excel data to SQLite with an additional result column."""
        excel_data[result_column] = None
        conn = sqlite3.connect(db_path)
        excel_data.to_sql('records', conn, if_exists='replace', index=False)
        conn.close()

    @staticmethod
    def execute_custom_script(db_path, script, batch_size=1):
        """Execute custom Python script on SQLite data."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM records")
        columns = [desc[0] for desc in cursor.description]

        def process_row(row):
            # Map row to a dictionary for the script
            record = dict(zip(columns, row))
            try:
                exec(script, {}, {"record": record})
                return tuple(record.values())
            except Exception as e:
                return None, str(e)

        new_rows = []
        for i, row in enumerate(cursor.fetchall()):
            if i % batch_size == 0 and new_rows:
                cursor.executemany("REPLACE INTO records VALUES (?)", new_rows)
                new_rows = []
            result = process_row(row)
            if result:
                new_rows.append(result)

        conn.commit()
        conn.close()
