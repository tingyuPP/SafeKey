from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHeaderView, QHBoxLayout, QTableWidgetItem, QApplication,
                            QFileDialog)
from qfluentwidgets import (SubtitleLabel, setFont, TableWidget, PrimaryPushButton, MessageBoxBase,
                            SearchLineEdit, LineEdit, CaptionLabel, StrongBodyLabel, PasswordLineEdit,
                            MessageBox, PushButton, ComboBox)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import Qt, QTimer
from qfluentwidgets import FluentIcon as FIF
import sqlite3
from database import DatabaseManager
from config import cfg
import os

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
        self.exportButton = PrimaryPushButton(FIF.LINK, '导出', self)
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
        self.passwordTable.verticalHeader().setVisible(False)
        self.passwordTable.setColumnHidden(0, True)  
        self.passwordTable.setSelectionBehavior(self.passwordTable.SelectRows)
        self.passwordTable.setSelectionMode(self.passwordTable.ExtendedSelection)

        # 在原有代码基础上进行优化
        original_style = self.passwordTable.styleSheet()

        enhancement_style = """
        /* 纯色边框选中效果 */
        QTableView::item:selected {
            border-top: 2px solid #0078D4;
            border-bottom: 2px solid #0078D4;
            background: transparent;
        }
        """

        # 智能合并样式（保留原有样式优先级）
        combined_style = f"""
        {original_style}
        {enhancement_style}
        """

        self.passwordTable.setStyleSheet(combined_style)
        # 延迟初始化列宽（等界面显示完成后）
        QTimer.singleShot(0, self.initializeColumnWidths)

        setFont(self.label, 24)
        # self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.hBoxLayout.addWidget(self.label, 0, Qt.AlignLeft)
        self.hBoxLayout.addWidget(self.uploadButton, 0, Qt.AlignLeft)
        self.hBoxLayout.addWidget(self.deleteButton, 0, Qt.AlignLeft)
        self.hBoxLayout.addWidget(self.exportButton, 0, Qt.AlignLeft)
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
        self.exportButton.clicked.connect(self.export_pass)
        self.passwordTable.cellDoubleClicked.connect(self.on_cell_double_clicked)
        self.passwordTable.cellChanged.connect(self.on_cell_changed)
        self.searchLineEdit.searchSignal.connect(self.search_passwords)
        self.searchLineEdit.clearSignal.connect(self.handle_clear)
        self.searchLineEdit.textChanged.connect(self.handle_realtime_search)
        self.editing_enabled = False # 防止初始化时触发修改


    def resizeEvent(self, event):
        """窗口缩放时自动调整列宽"""
        super().resizeEvent(event)
        self.initializeColumnWidths()
    
    def initializeColumnWidths(self):
        """自动调整列宽的核心方法"""
        table = self.passwordTable
        if table.width() < 400:  # 最小宽度保护
            return
        
        # 计算可用宽度（考虑滚动条）
        scrollbar = table.verticalScrollBar()
        available_width = table.width() - (scrollbar.width() if scrollbar.isVisible() else 0)
        
        # 设置列宽比例（网站:用户名:密码:备注 = 3:2:3:2）
        ratios = [0.3, 0.2, 0.3, 0.2]
        for col, ratio in zip(range(1,5), ratios):
            table.setColumnWidth(col, int(available_width * ratio))
            
        # 强制更新表格布局
        table.viewport().update()

    def on_cell_double_clicked(self, row, col):
        QApplication.instance().processEvents()
        if col in [1, 2, 3, 4]:  # 网站、用户名、密码、备注
            self.editing_enabled = True
            self.passwordTable.editItem(self.passwordTable.item(row, col))
    
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

    def get_selected_ids(self):
        selected_items = self.passwordTable.selectedItems()
        rows = {item.row() for item in selected_items}
        ids = []
        for row in rows:
            ids.append(int(self.passwordTable.item(row, 0).text()))
        return ids

    def delete_pass(self):
        # 获取选中ID
        selected_ids = self.get_selected_ids()
        
        if not selected_ids:
            MessageBox("提示", "请先选择要删除的记录", self.mainWindow).exec_()
            return

        # 确认对话框
        box = MessageBox(
            title="确认删除",
            content=f"确定要删除选中的 {len(selected_ids)} 条记录吗？",
            parent=self.mainWindow
        )
        if box.exec_():
            # 执行删除
            if self.db.delete_passwords(selected_ids):
                self.load_data()  # 刷新表格
                MessageBox("成功", "已删除选中的密码条目", self.mainWindow).exec_()
            else:
                MessageBox("错误", "删除记录时发生错误", self.mainWindow).exec_()

    def export_pass(self):
        w = ExportMessageBox(self.mainWindow, self)
        w.show()

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
        self.notesLabel = StrongBodyLabel('输入备注（可选）', self)
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

class ExportMessageBox(MessageBoxBase):
    def __init__(self, parent=None, interface=None):
        super().__init__(parent)
        self.interface = interface
        self.viewLayout.setSpacing(20)
        self.hboxLayout = QHBoxLayout(self)
        self.hboxLayout2 = QHBoxLayout(self)
        self.hboxLayout3 = QHBoxLayout(self)
        self.titleLabel = SubtitleLabel('导出密码到外部文件', self)
        self.pathLabel = StrongBodyLabel('导出路径：', self)
        self.pathLineEdit = LineEdit(self)
        self.pathLineEdit.resize(400, 30)
        self.pathLineEdit.setText(cfg.get(cfg.exportDir))
        self.fmtLabel = StrongBodyLabel('导出格式：', self)
        self.fmtCombo = ComboBox(self)
        items = ['CSV', 'JSON', 'AES']
        self.fmtCombo.addItems(items)
        self.fmtCombo.setPlaceholderText('选择导出格式')
        self.fmtCombo.setMaximumWidth(200)
        self.fmtCombo.setCurrentIndex(-1)
        self.browseButton = PushButton(FIF.FOLDER, '浏览文件夹', self)
        self.fileLabel = StrongBodyLabel('文件名：', self)
        self.fileLineEdit = LineEdit(self)
        self.fileLineEdit.setPlaceholderText('输入文件名（不含后缀）')
        self.fileLineEdit.setClearButtonEnabled(True)
        self.warningLabel = CaptionLabel("路径、文件名及格式不能为空")
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))
        self.warningLabel.hide()

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.pathLabel)
        self.hboxLayout.addWidget(self.pathLineEdit)
        self.hboxLayout.addWidget(self.browseButton)
        self.viewLayout.addLayout(self.hboxLayout)
        self.hboxLayout2.addWidget(self.fmtLabel)
        self.hboxLayout2.addWidget(self.fmtCombo, Qt.AlignLeft)
        self.hboxLayout2.addStretch(1)
        self.viewLayout.addLayout(self.hboxLayout2)
        self.hboxLayout3.addWidget(self.fileLabel)
        self.hboxLayout3.addWidget(self.fileLineEdit)
        self.viewLayout.addLayout(self.hboxLayout3)
        self.viewLayout.addWidget(self.warningLabel)
        
        self.widget.setMinimumWidth(500)
        self.yesButton.setText('导出')
        self.cancelButton.setText('取消')

        # 信号连接
        self.yesButton.clicked.disconnect()
        self.yesButton.clicked.connect(self._handle_export_passwords)
        self.browseButton.clicked.connect(self._handle_browse)
    
    def _handle_browse(self):
        """处理浏览文件夹逻辑"""
        path = QFileDialog.getExistingDirectory(self, "选择导出路径")
        if path:
            self.pathLineEdit.setText(path)

    def _handle_export_passwords(self):
        """处理导出密码逻辑"""
        if self.validate():
            path = self.pathLineEdit.text().strip()
            fmt = self.fmtCombo.currentText()
            file_name = self.fileLineEdit.text().strip()
            full_path = f"{path}/{file_name}.{fmt.lower()}"
            try:
                self.interface.db.export_passwords(full_path, fmt.lower())
                self.accept()
            except sqlite3.Error as e:
                MessageBox("错误", f"导出失败: {str(e)}", self).exec_()

    def validate(self):
        path = self.pathLineEdit.text().strip()
        fmt = self.fmtCombo.currentText()
        name = self.fileLineEdit.text().strip()
        
        # 基础非空检查
        if not all([path, fmt, name]):
            self.warningLabel.setText("所有字段均为必填项")
            self.warningLabel.show()
            return False
            
        # 路径有效性检查
        if not os.path.isdir(os.path.dirname(path)):
            self.warningLabel.setText("目录路径无效")
            self.warningLabel.show()
            return False
        
        # 检查是否存在同名文件
        if os.path.exists(f"{path}/{name}.{fmt.lower()}"):
            dialog = MessageBox("警告", "文件已存在，是否覆盖？", self)
            if not dialog.exec_():
                return False
            else:
                return True
            
        self.warningLabel.hide()
        return True  # 仅返回基础验证结果