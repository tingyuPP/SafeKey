import sqlite3
import csv
import json
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

    def delete_passwords(self, password_ids):
        """批量删除密码记录"""
        if not password_ids:
            return False
        
        try:
            with self.conn:  
                cursor = self.conn.cursor()
                placeholders = ','.join(['?'] * len(password_ids))
                query = f"DELETE FROM passwords WHERE id IN ({placeholders})"
                cursor.execute(query, tuple(password_ids))
            return True
        except sqlite3.Error as e:
            MessageBox.critical(None, "数据库错误", f"删除操作失败: {str(e)}")
            return False
        except Exception as e:
            MessageBox.critical(None, "意外错误", f"发生未预期错误: {str(e)}")
            return False

    def get_all_passwords(self):
        cursor = self.execute_query("SELECT * FROM passwords ORDER BY website ASC")
        return cursor.fetchall() if cursor else []

    def update_password(self, record_id, **kwargs):
        """更新密码记录"""
        if not kwargs:
            return
        
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(record_id)
        
        query = f"""
        UPDATE passwords 
        SET {set_clause}
        WHERE id = ?
        """
        self.conn.execute(query, values)
        self.conn.commit()

    def search_passwords(self, keyword):
        """根据关键词模糊搜索网站"""
        query = """
        SELECT * FROM passwords 
        WHERE website LIKE ?
        ORDER BY website ASC
        """
        cursor = self.conn.execute(query, (f"%{keyword}%",))
        return cursor.fetchall()
    
    def export_passwords(self, file_path, fmt):
        data = self.get_all_passwords()  # 假设已有该方法获取所有数据
        if fmt == 'csv':
            self._export_to_csv(file_path, data)
        elif fmt == 'json':
            self._export_to_json(file_path, data)
        elif fmt == 'aes':
            raise NotImplementedError("AES export not implemented yet")
        else:
            raise ValueError(f"Unsupported format: {fmt}")

    def _export_to_csv(self, file_path, data):
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Website', 'Username', 'Password', 'Notes'])
            for row in data:
                writer.writerow(row)

    def _export_to_json(self, file_path, data):
        entries = []
        for row in data:
            entry = {
                'id': row[0],
                'website': row[1],
                'username': row[2],
                'password': row[3],
                'notes': row[4]
            }
            entries.append(entry)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=4)

    def __del__(self):
        if self.conn:
            self.conn.close()
