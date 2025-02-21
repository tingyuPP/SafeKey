from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHeaderView, QHBoxLayout, QTableWidgetItem
from qfluentwidgets import (SubtitleLabel, setFont, TableWidget, PrimaryPushButton, MessageBoxBase,
                            SearchLineEdit)
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

    def init_ui(self, text):
        self.label = SubtitleLabel(text, self)
        self.vBoxLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout(self.vBoxLayout.widget())
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setSpacing(15)
        self.uploadButton = PrimaryPushButton(FIF.ADD, '增加', self.hBoxLayout.widget())
        self.deleteButton = PrimaryPushButton(FIF.DELETE, '删除', self.hBoxLayout.widget())
        self.searchLineEdit = SearchLineEdit(self.hBoxLayout.widget())
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

    def initializeColumnWidths(self):
        """初始化列宽（保持原有逻辑）"""
        if self.passwordTable.width() > 0:
            column_width = self.passwordTable.width() // 4
            for col in range(1, 5):  # 跳过隐藏的ID列
                self.passwordTable.setColumnWidth(col, column_width)

    # 加载数据
    def load_data(self):
        self.passwordTable.clearContents()
        records = self.db.get_all_passwords()
        self.passwordTable.setRowCount(len(records))

        for row, record in enumerate(records):
            for col, data in enumerate(record):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignCenter)
                # 密码列显示为星号
                if col == 3:
                    item = QTableWidgetItem("*" * 8)
                self.passwordTable.setItem(row, col, item)

    def upload_pass(self):
        pass

    def delete_pass(self):
        pass

class UpdateMessageBox(MessageBoxBase):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        pass
