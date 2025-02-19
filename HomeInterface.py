from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHeaderView
from qfluentwidgets import SubtitleLabel, setFont, TableWidget
from PyQt5.QtCore import Qt, QTimer


class HomeInterface(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.vBoxLayout = QVBoxLayout(self)
        self.passwordTable =TableWidget(self)
        self.passwordTable.setColumnCount(4)
        self.passwordTable.setBorderVisible(True)
        self.passwordTable.setBorderRadius(8)
        self.passwordTable.setWordWrap(False)
        self.passwordTable.setHorizontalHeaderLabels(['网站','用户名', '密码', '备注'])
        self.passwordTable.horizontalHeader().setVisible(True)
        # 设置列宽调整策略：允许用户手动调整
        header = self.passwordTable.horizontalHeader()
        header.setVisible(True)
        for col in range(4):
            header.setSectionResizeMode(col, QHeaderView.Interactive)
        
        # 延迟初始化列宽（等界面显示完成后）
        QTimer.singleShot(0, self.initializeColumnWidths)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.vBoxLayout.addWidget(self.label, 0, Qt.AlignLeft | Qt.AlignTop)
        self.vBoxLayout.addWidget(self.passwordTable, 1)
        self.setObjectName(text.replace(' ', '-'))

        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        self.vBoxLayout.setSpacing(20)
        self.label.setContentsMargins(20, 0, 0, 0)

    def initializeColumnWidths(self):
        """初始化时均分列宽"""
        if self.passwordTable.width() > 0:
            column_width = self.passwordTable.width() // 4
            for col in range(4):
                self.passwordTable.setColumnWidth(col, column_width)