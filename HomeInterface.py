from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHeaderView, QHBoxLayout, QTableWidgetItem
from qfluentwidgets import (SubtitleLabel, setFont, TableWidget, PrimaryPushButton, MessageBoxBase,
                            SearchLineEdit, LineEdit, CaptionLabel, StrongBodyLabel, PasswordLineEdit,
                            MessageBox)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import Qt, QTimer
from qfluentwidgets import FluentIcon as FIF
import sqlite3
from database import DatabaseManager

class HomeInterface(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.init_ui(text)
        self.db = DatabaseManager()
        self.load_data()
        self.mainWindow = parent

    def init_ui(self, text):
        self.label = SubtitleLabel(text, self)
        self.vBoxLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setSpacing(15)
        self.uploadButton = PrimaryPushButton(FIF.ADD, '增加', self)
        self.deleteButton = PrimaryPushButton(FIF.DELETE, '删除', self)
        self.searchLineEdit = SearchLineEdit(self)
        self.searchLineEdit.setPlaceholderText('搜索网站')
        self.passwordTable =TableWidget(self)
        self.passwordTable.setColumnCount(5)
        self.passwordTable.setBorderVisible(True)
        self.passwordTable.setBorderRadius(8)
        self.passwordTable.setWordWrap(False)
        self.passwordTable.setHorizontalHeaderLabels(['ID', '网站','用户名', '密码', '备注'])
        self.passwordTable.horizontalHeader().setVisible(True)
        self.passwordTable.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.passwordTable.setColumnHidden(0, True)  
        
        # 延迟初始化列宽（等界面显示完成后）
        QTimer.singleShot(0, self.initializeColumnWidths)

        setFont(self.label, 24)
        # self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.hBoxLayout.addWidget(self.label, 0, Qt.AlignLeft)
        self.hBoxLayout.addWidget(self.uploadButton, 0, Qt.AlignLeft)
        self.hBoxLayout.addWidget(self.deleteButton, 0, Qt.AlignLeft)
        self.hBoxLayout.addWidget(self.searchLineEdit, 0, Qt.AlignLeft)
        self.hBoxLayout.addStretch(1)

        self.vBoxLayout.addLayout(self.hBoxLayout)
        self.vBoxLayout.addWidget(self.passwordTable, 1)
        self.setObjectName(text.replace(' ', '-'))

        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        self.vBoxLayout.setSpacing(20)
        self.label.setContentsMargins(20, 0, 0, 0)

        # 信号连接
        self.uploadButton.clicked.connect(self.upload_pass)
        self.deleteButton.clicked.connect(self.delete_pass)
        self.passwordTable.cellDoubleClicked.connect(self.on_cell_double_clicked)
        self.passwordTable.cellChanged.connect(self.on_cell_changed)
        self.searchLineEdit.searchSignal.connect(self.search_passwords)
        self.searchLineEdit.clearSignal.connect(self.handle_clear)
        self.searchLineEdit.textChanged.connect(self.handle_realtime_search)
        self.editing_enabled = False # 防止初始化时触发修改
    
    def initializeColumnWidths(self):
        if self.passwordTable.width() > 0:
            column_width = self.passwordTable.width() // 4
            for col in range(1, 5):  # 跳过隐藏的ID列
                self.passwordTable.setColumnWidth(col, column_width)

    def on_cell_double_clicked(self, row, col):
        if col in [1, 2, 3, 4]:  # 网站、用户名、密码、备注
            self.editing_enabled = True
            self.passwordTable.editItem(self.passwordTable.item(row, col))
    
        # 新增方法：处理单元格修改
    def on_cell_changed(self, row, col):
        """处理单元格内容修改"""
        if not self.editing_enabled:
            return
        
        # 获取修改后的值
        new_value = self.passwordTable.item(row, col).text().strip()
        # 获取记录ID
        record_id = int(self.passwordTable.item(row, 0).text())
        
        # 映射列到数据库字段
        column_mapping = {
            1: "website",
            2: "username",
            3: "password",
            4: "notes"
        }
        
        if col not in column_mapping:
            return
        
        # 数据验证
        if col in [1, 2, 3] and not new_value:  # 网站和用户名不能为空
            MessageBox("警告", "网站、用户名及密码不能为空", self).exec_()
            self.load_data()  # 重置表格数据
            return
        
        try:
            self.db.update_password(
                record_id=record_id,
                **{column_mapping[col]: new_value}
            )
        except sqlite3.Error as e:
            MessageBox("错误", f"数据库更新失败: {str(e)}", self).exec_()
            self.load_data()  # 回滚表格数据

        self.editing_enabled = False  # 重置状态

    def handle_realtime_search(self):
        """ 实时搜索处理 """
        keyword = self.searchLineEdit.text().strip()
        self.search_passwords(keyword)

    def search_passwords(self, keyword):
        """根据关键词搜索密码记录"""
        try:
            records = self.db.search_passwords(keyword)
            self._update_table_data(records)
        except sqlite3.Error as e:
            MessageBox("错误", f"搜索失败: {str(e)}", self).exec_()
    
    def handle_clear(self):
        """清空搜索框"""
        self.load_data()

    def _update_table_data(self, records):
        """通用表格更新方法"""
        self.passwordTable.clearContents()
        self.passwordTable.setRowCount(len(records))
        
        for row, record in enumerate(records):
            for col, data in enumerate(record):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignCenter)
                self.passwordTable.setItem(row, col, item)

    def load_data(self):
        """加载全部数据（重构成通用方法）"""
        try:
            records = self.db.get_all_passwords()
            self._update_table_data(records)
        except sqlite3.Error as e:
            MessageBox("错误", f"数据加载失败: {str(e)}", self).exec_()

    def upload_pass(self):
        w = UpdateMessageBox(self.mainWindow, self)
        w.show()

    def delete_pass(self):
        pass

class UpdateMessageBox(MessageBoxBase):

    def __init__(self, parent=None, interface=None):
        super().__init__(parent)
        self.parent_interface = interface
        self.titleLabel = SubtitleLabel('添加密码', self)
        self.webLabel = StrongBodyLabel('输入网站', self)
        self.webLineEdit = LineEdit(self)
        self.webLineEdit.setPlaceholderText('输入网站')
        self.webLineEdit.setClearButtonEnabled(True)
        self.usernameLabel = StrongBodyLabel('输入用户名', self)
        self.usernameLineEdit = LineEdit(self)
        self.usernameLineEdit.setPlaceholderText('输入用户名')
        self.usernameLineEdit.setClearButtonEnabled(True)
        self.passwordLabel = StrongBodyLabel('输入密码', self)
        self.passwordLineEdit = PasswordLineEdit(self)
        self.passwordLineEdit.setPlaceholderText('输入密码')
        self.passwordLineEdit.setClearButtonEnabled(True)
        self.notesLabel = StrongBodyLabel('输入备注', self)
        self.notesLineEdit = LineEdit(self)
        self.notesLineEdit.setPlaceholderText('输入备注')
        self.notesLineEdit.setClearButtonEnabled(True)
        self.warningLabel = CaptionLabel("网站，用户名和密码不能为空")
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.webLabel)
        self.viewLayout.addWidget(self.webLineEdit)
        self.viewLayout.addWidget(self.usernameLabel)
        self.viewLayout.addWidget(self.usernameLineEdit)
        self.viewLayout.addWidget(self.passwordLabel)
        self.viewLayout.addWidget(self.passwordLineEdit)
        self.viewLayout.addWidget(self.notesLabel)
        self.viewLayout.addWidget(self.notesLineEdit)
        self.viewLayout.addWidget(self.warningLabel)
        self.warningLabel.hide()
    
        self.widget.setMinimumWidth(350)
        self.yesButton.setText('添加')
        self.cancelButton.setText('取消')

        # 信号连接
        self.yesButton.clicked.connect(self._handle_add_password)

    def _handle_add_password(self):
        """处理添加密码逻辑"""
        if self.validate():
            # 获取输入内容
            web = self.webLineEdit.text().strip()
            username = self.usernameLineEdit.text().strip()
            password = self.passwordLineEdit.text().strip()
            notes = self.notesLineEdit.text().strip()

            # 调用父窗口的数据库方法插入数据
            try:
                self.parent_interface.db.add_password(
                    website=web,
                    username=username,
                    password=password,
                    notes=notes
                )
                # 清空输入框
                self._clear_inputs()
                # 关闭对话框
                self.accept()
                # 刷新父界面数据
                self.parent_interface.load_data()
            except sqlite3.Error as e:
                # 处理数据库错误
                self._show_error_message(f"数据库错误: {str(e)}")
    
    def _clear_inputs(self):
        """清空输入框内容"""
        self.webLineEdit.clear()
        self.usernameLineEdit.clear()
        self.passwordLineEdit.clear()
        self.notesLineEdit.clear()

    def _show_error_message(self, text):
        """显示错误提示"""
        self.warningLabel.setText(text)
        self.warningLabel.show()

    def validate(self):
        web = self.webLineEdit.text()
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()
        notes = self.notesLineEdit.text()
        if not web or not username or not password:
            isValid = False
        else:
            isValid = True
        self.warningLabel.setHidden(isValid)
        return isValid    
