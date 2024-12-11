import pandas as pd
import sqlite3
from typing import List, Dict
import os
from jd_huicai import fetch_price_from_wanbang, batch_fetch_prices, extract_number


class DataProcessor:
    def __init__(self, excel_path: str, db_path: str, batch_size: int = 100):
        """
        初始化数据处理器
        :param excel_path: Excel文件路径
        :param db_path: SQLite数据库路径
        :param batch_size: 批处理大小
        """
        self.excel_path = excel_path
        self.db_path = db_path
        self.batch_size = batch_size
        self.conn = None
        self.cursor = None
        self.connect_db()

    def connect_db(self):
        """建立数据库连接"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close_db(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

    def import_excel_to_sqlite(
        self, table_name: str, additional_columns: Dict[str, str]
    ):
        """
        将Excel数据导入SQLite，并添加额外的列
        :param table_name: 表名
        :param additional_columns: 额外列的配置 {'column_name': 'column_type'}
        """
        try:
            # 读取Excel文件
            df = pd.read_excel(self.excel_path)

            # 连接数据库
            # self.connect_db()

            # 创建表（包含额外的列）
            columns = []
            for col in df.columns:
                columns.append(f'"{col}" TEXT')

            # 添加额外的列
            for col_name, col_type in additional_columns.items():
                columns.append(f'"{col_name}" {col_type}')

            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {', '.join(columns)}
            )
            """
            self.cursor.execute(create_table_sql)

            # 将DataFrame数据导入SQLite
            df.to_sql(table_name, self.conn, if_exists="append", index=False)

            self.conn.commit()
            print(f"Successfully imported Excel data to {table_name}")

        except Exception as e:
            print(f"Error importing Excel: {str(e)}")
            raise

    def process_data_in_batches(self, table_name: str, process_func):
        """
        批量处理数据
        :param table_name: 表名
        :param process_func: 处理函数，接收一批数据，返回处理结果
        """
        try:
            # 获取总记录数
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_records = self.cursor.fetchone()[0]

            # 批量处理数据
            for offset in range(0, total_records, self.batch_size):
                # 获取一批数据
                query = f"SELECT * FROM {table_name} LIMIT {self.batch_size} OFFSET {offset}"
                batch_data = pd.read_sql_query(query, self.conn)

                # 处理数据
                processed_results = process_func(batch_data)

                # 更新处理结果到数据库
                for index, row in batch_data.iterrows():
                    update_columns = []
                    update_values = []

                    for key, value in processed_results[index].items():
                        update_columns.append(f"{key} = ?")
                        update_values.append(value)
                    if len(update_values) == 0:
                        continue
                    update_sql = f"""
                    UPDATE {table_name}
                    SET {', '.join(update_columns)}
                    WHERE id = ?
                    """
                    update_values.append(row["id"])

                    self.cursor.execute(update_sql, update_values)

                self.conn.commit()
                print(
                    f"Processed batch: {offset} to {min(offset + self.batch_size, total_records)}"
                )

        except Exception as e:
            print(f"Error processing data: {str(e)}")
            raise


def example_usage(overwrite: bool = False, run_huicai: bool = False):
    """
    示例使用
    :param overwrite: 如果为True，则在处理前删除已存在的数据库文件
    """
    db_path = "本周市调清单.db"
    processor = DataProcessor(
        excel_path="/Users/dingjz/Downloads/本周市调清单底表.xlsx",
        db_path=db_path,
        batch_size=1,
    )

    # 定义额外的列
    additional_columns = {
        "processed_result": "TEXT",
        "processing_date": "DATETIME",
        "价格来源": "TEXT",
        "status": "INTEGER",
    }

    # 如果需要覆盖且数据库文件存在，则删除它
    if overwrite:
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Removed existing database: {db_path}")
        # 导入Excel数据
        processor.import_excel_to_sqlite("my_table", additional_columns)

    # 示例处理函数
    def process_batch(batch_data):
        # 先批量调用慧采的接口，把结果解析出来，失败的再去调用万邦的接口
        # 慧采应该返回每条的结果，如果某条的结果是失败，就把结果置为失败，然后再去调用万邦的接口

        results = {}
        sku_ids = []
        # fetch_price_from_wanbang()
        for index, row in batch_data.iterrows():
            sku_id = extract_number(row["*网站商品唯一标识"])
            sku_ids.append(sku_id)
            results[index] = {}
            if row["status"] == 0:
                wanbang_res = fetch_price_from_wanbang(sku_id)
                if wanbang_res["status"] == "success":
                    results[index] = {
                        "processed_result": wanbang_res["price"],
                        "status": 1,
                        "价格来源": "万邦",
                        "processing_date": pd.Timestamp.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    }
                    continue
                print(f"{sku_id}万邦失败:{wanbang_res['error_message']}")
                # 都失败了，就置为失败
                results[index] = {
                    "processed_result": "",
                    "status": 0,
                    "价格来源": "万邦",
                    "processing_date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
        # if run_huicai:
        # huicai_res = batch_fetch_prices(sku_ids)
        # for idx, res in huicai_res.items():
        #     sku_id = sku_ids[idx]
        #     if res["status"] == "success":
        #         results[idx] = {
        #             "processed_result": res["price"],
        #             "status": 1,
        #             "价格来源": "慧采",
        #             # processing_date为当前时间
        #             "processing_date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        #         }
        #         continue
        #     results[idx] = {
        #         "processed_result": "慧采没有",
        #         "status": 0,
        #         "价格来源": "慧采",
        #         "processing_date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        #     }
        #     print(f"{sku_id}慧采失败:{res['error_message']}")

        return results

    # 处理数据
    processor.process_data_in_batches("my_table", process_batch)

    # 关闭数据库连接
    processor.close_db()


if __name__ == "__main__":
    run_huicai = False
    example_usage(overwrite=False, run_huicai=run_huicai)  # 设置是否覆盖现有数据库
