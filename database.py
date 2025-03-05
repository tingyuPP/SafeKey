import sqlite3
import csv
import json
from qfluentwidgets import MessageBox
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from config import cfg

class DatabaseManager:
    def __init__(self, db_name="passwords.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

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

    def add_password(self, website, username, password, notes="", override=True):
        """添加密码记录"""
        if override:
            query = "SELECT id FROM passwords WHERE website=? AND username=? AND password=?"
            cursor = self.conn.execute(query, (website, username, password))
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    del_query = "DELETE FROM passwords WHERE id=?"
                    self.conn.execute(del_query, (row[0],))
                self.conn.commit()
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
        data = self.get_all_passwords()
        if fmt == 'csv':
            self._export_to_csv(file_path, data)
        elif fmt == 'json':
            self._export_to_json(file_path, data)
        elif fmt == 'aes':
            self._export_to_aes(file_path, data)
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
    
    def _export_to_aes(self, file_path, data):
        # 将数据转换为 JSON 格式
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
        json_data = json.dumps(entries, indent=4).encode('utf-8')

        key = b'Sixteen byte key'      
        iv = get_random_bytes(AES.block_size)  
        cipher = AES.new(key, AES.MODE_CBC, iv)
        cipherText = cipher.encrypt(pad(json_data, AES.block_size))

        # 将 IV 和密文保存到文件。解密时需要从文件中读取前16个字节作为 IV
        with open(file_path, 'wb') as f:
            f.write(iv)
            f.write(cipherText)
    
    def import_passwords(self, file_path, fmt):
        if fmt == 'csv':
            self._import_from_csv(file_path)
        elif fmt == 'json':
            self._import_from_json(file_path)
        elif fmt == 'aes':
            self._import_from_aes(file_path)
        else:
            raise ValueError(f"Unsupported format: {fmt}")

    def _import_from_csv(self, file_path):
        if cfg.get(cfg.importSetting) == "Skip":
            override = False
        else:
            override = True
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)  # 跳过表头
            for row in reader:
                if len(row) < 4:
                    continue
                website = row[1]
                username = row[2]
                password = row[3]
                notes = row[4] if len(row) >= 5 else ""
                self.add_password(website, username, password, notes, override)

    def _import_from_json(self, file_path):
        if cfg.get(cfg.importSetting) == "Skip":
            override = False
        else:
            override = True
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for entry in data:
                website = entry.get('website', "")
                username = entry.get('username', "")
                password = entry.get('password', "")
                notes = entry.get('notes', "")
                self.add_password(website, username, password, notes, override)

    def _import_from_aes(self, file_path):
        if cfg.get(cfg.importSetting) == "Skip":
            override = False
        else:
            override = True
        with open(file_path, 'rb') as f:
            # 读取前16字节作为 IV
            iv = f.read(16)  
            cipherText = f.read()
        key = b'Sixteen byte key'
        cipher = AES.new(key, AES.MODE_CBC, iv)
        from Crypto.Util.Padding import unpad
        decrypted = unpad(cipher.decrypt(cipherText), AES.block_size)
        json_data = decrypted.decode('utf-8')
        data = json.loads(json_data)
        for entry in data:
            website = entry.get('website', "")
            username = entry.get('username', "")
            password = entry.get('password', "")
            notes = entry.get('notes', "")
            self.add_password(website, username, password, notes, override)

    def __del__(self):
        if self.conn:
            self.conn.close()
