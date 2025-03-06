from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHeaderView, QHBoxLayout, QTableWidgetItem, QApplication,
                            QFileDialog)
from qfluentwidgets import (SubtitleLabel, setFont, TableWidget, PrimaryPushButton, MessageBoxBase,
                            SearchLineEdit, LineEdit, CaptionLabel, StrongBodyLabel, PasswordLineEdit,
                            MessageBox, PushButton, ComboBox, InfoBar, InfoBarPosition, DropDownToolButton,
                            RoundMenu, Action)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import Qt, QTimer
from qfluentwidgets import FluentIcon as FIF
import sqlite3
from Database import DatabaseManager
from config import cfg
import os

class HomeInterface(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.vBoxLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout(self)
        self.uploadButton = PrimaryPushButton(FIF.ADD, '增加', self)
        self.deleteButton = PrimaryPushButton(FIF.DELETE, '删除', self)
        self.fileButton = DropDownToolButton(FIF.FOLDER)
        self.fileMenu = RoundMenu(parent=self.fileButton)
        self.searchLineEdit = SearchLineEdit(self)
        self.passwordTable =TableWidget(self)
        self.db = DatabaseManager()
        self.__initWidget(text)
        self.__initLayout(text)
        self.load_data()
        self.mainWindow = parent

    def __initWidget(self, text):
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setSpacing(15)
        self.searchLineEdit.setPlaceholderText('搜索网站')
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
        self.fileButton.setMenu(self.fileMenu)
        self.fileMenu.addAction(Action(FIF.FOLDER_ADD, '导入', triggered=lambda: self.import_pass()))
        self.fileMenu.addAction(Action(FIF.SAVE, '导出', triggered=lambda: self.export_pass()))
        original_style = self.passwordTable.styleSheet()
        self.passwordTable.setStyleSheet(original_style)

        # 延迟初始化列宽，避免出现列宽异常
        QTimer.singleShot(0, self.initializeColumnWidths)
        setFont(self.label, 24)
        self.setObjectName(text.replace(' ', '-'))
        self.label.setContentsMargins(20, 0, 0, 0)

        # 信号连接
        self.uploadButton.clicked.connect(self.upload_pass)
        self.deleteButton.clicked.connect(self.delete_pass)
        self.passwordTable.cellDoubleClicked.connect(self.on_cell_double_clicked)
        self.passwordTable.cellChanged.connect(self.on_cell_changed)
        self.searchLineEdit.searchSignal.connect(self.search_passwords)
        self.searchLineEdit.clearSignal.connect(self.handle_clear)
        self.searchLineEdit.textChanged.connect(self.handle_realtime_search)
        self.editing_enabled = False 

    def __initLayout(self, text):
        self.hBoxLayout.addWidget(self.label, 0, Qt.AlignLeft)
        self.hBoxLayout.addWidget(self.uploadButton, 0, Qt.AlignLeft)
        self.hBoxLayout.addWidget(self.deleteButton, 0, Qt.AlignLeft)
        self.hBoxLayout.addWidget(self.searchLineEdit, 0, Qt.AlignLeft)
        self.hBoxLayout.addWidget(self.fileButton, 0, Qt.AlignLeft)
        self.hBoxLayout.addStretch(1)
        self.vBoxLayout.addLayout(self.hBoxLayout)
        self.vBoxLayout.addWidget(self.passwordTable, 1)
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        self.vBoxLayout.setSpacing(20)

    def resizeEvent(self, event):
        """窗口缩放时自动调整列宽"""
        super().resizeEvent(event)
        self.initializeColumnWidths()
    
    def initializeColumnWidths(self):
        """自动调整列宽"""
        table = self.passwordTable
        if table.width() < 400:  
            return
        scrollbar = table.verticalScrollBar()
        available_width = table.width() - (scrollbar.width() if scrollbar.isVisible() else 0)

        # 设置列宽比例（网站:用户名:密码:备注 = 3:2:3:2）
        ratios = [0.3, 0.2, 0.3, 0.2]
        for col, ratio in zip(range(1,5), ratios):
            table.setColumnWidth(col, int(available_width * ratio))
        table.viewport().update()

    def on_cell_double_clicked(self, row, col):
        """处理单元格双击事件"""
        QApplication.instance().processEvents()
        # 网站、用户名、密码、备注
        if col in [1, 2, 3, 4]:            
            self.editing_enabled = True
            self.passwordTable.editItem(self.passwordTable.item(row, col))
    
    def on_cell_changed(self, row, col):
        """处理单元格内容修改"""
        if not self.editing_enabled:
            return
        new_value = self.passwordTable.item(row, col).text().strip()
        record_id = int(self.passwordTable.item(row, 0).text())
        column_mapping = {
            1: "website",
            2: "username",
            3: "password",
            4: "notes"
        }
        
        if col not in column_mapping:
            return

        if col in [1, 2, 3] and not new_value: 
            MessageBox("警告", "网站、用户名及密码不能为空", self.mainWindow).exec_()
            self.load_data()  
            return
        
        try:
            self.db.update_password(
                record_id=record_id,
                **{column_mapping[col]: new_value}
            )
        except sqlite3.Error as e:
            MessageBox("错误", f"数据库更新失败: {str(e)}", self.mainWindow).exec_()
            self.load_data()  

        self.editing_enabled = False  

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
        """显示添加密码的消息框"""
        w = UpdateMessageBox(self.mainWindow, self)
        w.show()

    def get_selected_ids(self):
        """获取选中的ID"""
        selected_items = self.passwordTable.selectedItems()
        rows = {item.row() for item in selected_items}
        ids = []
        for row in rows:
            ids.append(int(self.passwordTable.item(row, 0).text()))
        return ids

    def delete_pass(self):
        """删除密码记录"""
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
                self.load_data()  
                w = InfoBar.success(
                    title = "成功",
                    content="已成功删除所选的密码",
                    orient=Qt.Vertical,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=2000,
                    parent=self.mainWindow
                )
                w.show()
            else:
                w = InfoBar.error(
                    title = "错误",
                    content="删除失败",
                    orient=Qt.Vertical,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=2000,
                    parent=self.mainWindow
                )
                w.show()

    def export_pass(self):
        """显示导出密码的消息框"""
        w = ExportMessageBox(self.mainWindow, self)
        w.show()

    def import_pass(self):
        """导入密码"""
        w = QFileDialog.getOpenFileName(self, "选择文件", "", "CSV Files (*.csv);;JSON Files (*.json);;AES Files (*.aes)")
        if w[0]:
            try:
                print(w[0], w[1].split()[0].lower())
                self.db.import_passwords(w[0], w[1].split()[0].lower())
                self.load_data()
                w = InfoBar.success(
                    title = "成功",
                    content="密码已导入",
                    orient=Qt.Vertical,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=2000,
                    parent=self.mainWindow
                )
            except sqlite3.Error as e:
                w = InfoBar.error(
                    title = "错误",
                    content=f"导入失败: {str(e)}",
                    orient=Qt.Vertical,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=2000,
                    parent=self.mainWindow
                )
            
class UpdateMessageBox(MessageBoxBase):
    def __init__(self, parent=None, interface=None):
        super().__init__(parent)
        self.parent_interface = interface
        self.titleLabel = SubtitleLabel('添加密码', self)
        self.webLabel = StrongBodyLabel('输入网站', self)
        self.webLineEdit = LineEdit(self)
        self.usernameLabel = StrongBodyLabel('输入用户名', self)
        self.usernameLineEdit = LineEdit(self)
        self.passwordLabel = StrongBodyLabel('输入密码', self)
        self.passwordLineEdit = PasswordLineEdit(self)
        self.notesLabel = StrongBodyLabel('输入备注（可选）', self)
        self.notesLineEdit = LineEdit(self)
        self.warningLabel = CaptionLabel("网站，用户名和密码不能为空")
        self.__initWidget()
        self.__initLayout()
        

    def __initWidget(self):
        self.webLineEdit.setPlaceholderText('输入网站')
        self.webLineEdit.setClearButtonEnabled(True)
        self.usernameLineEdit.setPlaceholderText('输入用户名')
        self.usernameLineEdit.setClearButtonEnabled(True)
        self.passwordLineEdit.setPlaceholderText('输入密码')
        self.passwordLineEdit.setClearButtonEnabled(True)
        self.notesLineEdit.setPlaceholderText('输入备注')
        self.notesLineEdit.setClearButtonEnabled(True)
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))
        self.warningLabel.hide()
        self.widget.setMinimumWidth(350)
        self.yesButton.setText('添加')
        self.cancelButton.setText('取消')

        # 信号连接
        self.yesButton.clicked.connect(self._handle_add_password)

    def __initLayout(self):
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

    def _handle_add_password(self):
        """处理添加密码逻辑"""
        # 判断是否要覆盖原条目
        if cfg.get(cfg.importSetting) == "Skip":
            override = False
        else:
            override = True

        if self.validate():
            web = self.webLineEdit.text().strip()
            username = self.usernameLineEdit.text().strip()
            password = self.passwordLineEdit.text().strip()
            notes = self.notesLineEdit.text().strip()

            try:
                self.parent_interface.db.add_password(
                    website=web,
                    username=username,
                    password=password,
                    notes=notes,
                    override=override
                )
                self._clear_inputs()
                self.accept()
                w = InfoBar.success(
                    title = "成功",
                    content="已成功添加密码",
                    orient=Qt.Vertical,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=2000,
                    parent=self.parent_interface.mainWindow
                )
                w.show()
                self.parent_interface.load_data()
            except sqlite3.Error as e:
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
        """验证输入"""
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
        self.hboxLayout = QHBoxLayout(self)
        self.hboxLayout2 = QHBoxLayout(self)
        self.hboxLayout3 = QHBoxLayout(self)
        self.titleLabel = SubtitleLabel('导出密码到外部文件', self)
        self.pathLabel = StrongBodyLabel('导出路径：', self)
        self.pathLineEdit = LineEdit(self)
        self.fmtLabel = StrongBodyLabel('导出格式：', self)
        self.fmtCombo = ComboBox(self)
        self.browseButton = PushButton(FIF.FOLDER, '浏览文件夹', self)
        self.fileLabel = StrongBodyLabel('文件名：', self)
        self.fileLineEdit = LineEdit(self)
        self.warningLabel = CaptionLabel("路径、文件名及格式不能为空")
        self.__initWidget()
        self.__initLayout()

    def __initWidget(self):
        self.viewLayout.setSpacing(20)
        self.pathLineEdit.resize(400, 30)
        self.pathLineEdit.setText(cfg.get(cfg.exportDir))
        items = ['CSV', 'JSON', 'AES']
        self.fmtCombo.addItems(items)
        self.fmtCombo.setPlaceholderText('选择导出格式')
        self.fmtCombo.setMaximumWidth(200)
        self.fmtCombo.setCurrentIndex(-1)
        self.fileLineEdit.setPlaceholderText('输入文件名（不含后缀）')
        self.fileLineEdit.setClearButtonEnabled(True)
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))
        self.warningLabel.hide()
        self.widget.setMinimumWidth(500)
        self.yesButton.setText('导出')
        self.cancelButton.setText('取消')

        # 信号连接
        self.yesButton.clicked.disconnect()
        self.yesButton.clicked.connect(self._handle_export_passwords)
        self.browseButton.clicked.connect(self._handle_browse)

    def __initLayout(self):
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
                w = InfoBar.success(
                    title = "成功",
                    content="密码已导出到文件",
                    orient=Qt.Vertical,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=2000,
                    parent=self.interface.mainWindow
                )
                w.show()
            except sqlite3.Error as e:
                MessageBox("错误", f"导出失败: {str(e)}", self).exec_()

    def validate(self):
        """验证输入"""
        path = self.pathLineEdit.text().strip()
        fmt = self.fmtCombo.currentText()
        name = self.fileLineEdit.text().strip()
        
        # 检查是否有空字段
        if not all([path, fmt, name]):
            self.warningLabel.setText("所有字段均为必填项")
            self.warningLabel.show()
            return False
            
        # 路径有效性检查
        if not os.path.isdir(path):
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
        return True