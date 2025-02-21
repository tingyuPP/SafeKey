import sqlite3
from qfluentwidgets import MessageBox

class DatabaseManager:
    def __init__(self, db_name="passwords.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()
        print(1)

    # 建表
    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            notes TEXT
        )
        """
        self.execute_query(query)

    # 查询
    def execute_query(self, query, params=(), commit=False):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            if commit:
                self.conn.commit()
            return cursor
        except sqlite3.Error as e:
            MessageBox.critical(None, "数据库错误", f"数据库操作失败: {str(e)}")
            return None

    # 添加条目
    def add_password(self, website, username, password, notes=""):
        query = """
        INSERT INTO passwords (website, username, password, notes)
        VALUES (?, ?, ?, ?)
        """
        self.execute_query(query, (website, username, password, notes), commit=True)

    # 删除条目
    def delete_password(self, password_id):
        """根据ID删除记录"""
        query = "DELETE FROM passwords WHERE id = ?"
        self.execute_query(query, (password_id,), commit=True)

    # 获取所有密码
    def get_all_passwords(self):
        cursor = self.execute_query("SELECT * FROM passwords")
        return cursor.fetchall() if cursor else []

    def __del__(self):
        if self.conn:
            self.conn.close()
