from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget
from qfluentwidgets import (SubtitleLabel, setFont, HeaderCardWidget, ComboBox, StrongBodyLabel, CaptionLabel,
                            PrimaryPushButton, InfoBar ,HorizontalSeparator, LineEdit, InfoBarPosition,
                            ProgressBar, SingleDirectionScrollArea, CheckBox, SpinBox, CompactSpinBox,
                            SwitchButton, TextBrowser)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt
import string
import random

class ToolInterface(SingleDirectionScrollArea):
    def __init__(self, text : str, parent = None):
        super().__init__(parent = parent)
        self.mainWindow = parent
        self.label = SubtitleLabel(text, self)
        self.scrollWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)
        self.vBoxLayout.setSpacing(10)
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        self.easyPassGenerator = EasyPassGenerator(self)
        self.complexPassGenerator = ComplexPassGenerator(self)
        self.complexPassGenerator.setContentsMargins(0, 50, 0, 0)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setContentsMargins(20, 0, 0, 0)

        self.vBoxLayout.addWidget(self.label, 0, Qt.AlignLeft | Qt.AlignTop)
        self.vBoxLayout.addWidget(self.easyPassGenerator, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.complexPassGenerator, 0, Qt.AlignTop)
        self.vBoxLayout.addStretch(1)
        self.setObjectName(text.replace(' ', '-'))
        self.enableTransparentBackground()

class EasyPassGenerator(HeaderCardWidget):  
    def __init__(self, parent = None):
        super().__init__(parent = parent)
        self.interface = parent
        self.mainWindow = parent.mainWindow
        self.setTitle("简易密码生成器")
        self.setBorderRadius(8)
        # 常用易记单词列表（可自行扩展）
        self.word_list = [
            "apple", "river", "sun", "moon", "tree",
            "cloud", "happy", "music", "panda", "coffee",
            "beach", "smile", "guitar", "purple", "cookie"
        ]
        # 易混淆字符排除列表
        self.ambiguous_chars = {'l', '1', 'I', 'O', '0'}

        self.typeLabel = StrongBodyLabel("密码类别", self)
        # self.typedDescription = CaptionLabel("简单选择生成密码的类型", self)
        self.generateButton = PrimaryPushButton(FIF.PLAY_SOLID,"生成密码")
        # self.hintIcon = IconWidget(InfoBarIcon.INFORMATION)
        self.hintLabel = StrongBodyLabel("点击生成密码按钮以随机生成密码")
        # self.hintIcon.setFixedSize(24, 24)
        self.separator = HorizontalSeparator()
        self.separator.setContentsMargins(0, 0, 0, 0)
        self.resultLabel = StrongBodyLabel("生成结果", self)
        self.resultLineEdit = LineEdit(self)
        self.resultLineEdit.setReadOnly(True)
        self.copyButton = PrimaryPushButton(FIF.COPY, "复制")

        self.comboBox = ComboBox(self)
        self.comboBox.addItems(["高强度", "易记忆"])
        self.comboBox.setFixedWidth(320)

        self.strengthLabel = StrongBodyLabel("密码强度", self)
        self.strengthBarLabel = StrongBodyLabel("", self)
        self.strengthBarLabel.hide()
        self.strengthBar = ProgressBar(self)
        self.strengthBar.setFixedHeight(8)
        self.strengthBar.setFixedWidth(320)
        self.strengthBar.setUseAni(False)

        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.setSpacing(20)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout = QHBoxLayout()
        self.hBoxLayout2 = QHBoxLayout()
        self.hBoxLayout3 = QHBoxLayout()
        self.hBoxLayout4 = QHBoxLayout()

        self.hBoxLayout.addWidget(self.typeLabel)
        self.hBoxLayout.addWidget(self.comboBox)
        self.vBoxLayout.addLayout(self.hBoxLayout)
        # self.hBoxLayout2.addWidget(self.hintIcon, 0, Qt.AlignLeft)
        self.hBoxLayout2.addWidget(self.hintLabel, 0, Qt.AlignLeft)
        self.hBoxLayout2.addStretch(1)
        self.hBoxLayout2.addWidget(self.generateButton, 0, Qt.AlignRight)
        
        self.vBoxLayout.addLayout(self.hBoxLayout2)
        self.vBoxLayout.addWidget(self.separator)
        self.hBoxLayout3.addWidget(self.resultLabel)
        self.hBoxLayout3.addWidget(self.resultLineEdit)
        self.hBoxLayout3.addWidget(self.copyButton)
        self.vBoxLayout.addLayout(self.hBoxLayout3)

        self.hBoxLayout4.addWidget(self.strengthLabel, 0, Qt.AlignLeft)
        self.hBoxLayout4.addWidget(self.strengthBar, 0, Qt.AlignLeft)
        self.hBoxLayout4.addWidget(self.strengthBarLabel, 0, Qt.AlignLeft)
        self.hBoxLayout4.addStretch(1)
        self.vBoxLayout.addLayout(self.hBoxLayout4)

        self.viewLayout.addLayout(self.vBoxLayout)

        # 信号绑定
        self.generateButton.clicked.connect(self.easy_pass_generate)
        self.copyButton.clicked.connect(self.copy_password)

    def easy_pass_generate(self):
        if self.comboBox.currentText() == "高强度":
            password = self.generate_strong()
            self.resultLineEdit.setText("".join(password))
            self.strengthBar.setValue(100)
            self.strengthBar.setCustomBarColor("#00FF00", "#00FF00")
            self.strengthBarLabel.setText("强")
            self.strengthBarLabel.show()
        else:
            password = self.generate_memorable()
            self.resultLineEdit.setText("".join(password))
            self.strengthBar.setValue(33)
            self.strengthBar.setCustomBarColor("#FF0000", "#FF0000")
            self.strengthBarLabel.setText("弱")
            self.strengthBarLabel.show()

    def generate_strong(self, length=16):
        """生成高强度密码（默认16位）"""
        # 定义字符集
        uppercase = [c for c in string.ascii_uppercase if c not in self.ambiguous_chars]
        lowercase = [c for c in string.ascii_lowercase if c not in self.ambiguous_chars]
        digits = [c for c in string.digits if c not in self.ambiguous_chars]
        symbols = ['@', '#', '$', '%', '&', '*', '+', '-', '=']
        
        # 确保每个字符集至少包含一个字符
        password = [
            random.choice(uppercase),
            random.choice(lowercase),
            random.choice(digits),
            random.choice(symbols)
        ]
        
        # 填充剩余长度
        all_chars = uppercase + lowercase + digits + symbols
        password += random.choices(all_chars, k=length-4)
        
        random.shuffle(password)
        return ''.join(password)
    
    def generate_memorable(self, words=2, digits=2):
        selected = random.sample(self.word_list, words)
        numbers = str(random.randint(10**(digits-1), 10**digits-1))
        return ''.join(selected) + numbers

    def copy_password(self):
        self.resultLineEdit.selectAll()
        self.resultLineEdit.copy()
        self.resultLineEdit.deselect()
        w = InfoBar.success(
            title = "复制成功",
            content="密码已成功复制到剪贴板",
            orient=Qt.Vertical,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=2000,
            parent=self.mainWindow
        )
        w.show()

class ComplexPassGenerator(HeaderCardWidget):
    def __init__(self, parent = None):
        super().__init__(parent = parent)
        self.interface = parent
        self.mainWindow = parent.mainWindow
        self.setTitle("高级密码生成器")
        self.setBorderRadius(8)

        self.charLabel = StrongBodyLabel("使用字符", self)
        self.charCheckBoxContainer = QHBoxLayout()
        self.charCheckBoxContainer.setSpacing(10)
        self.charCheckBox1 = CheckBox("ABC")
        self.charCheckBox2 = CheckBox("abc")
        self.charCheckBox3 = CheckBox("123")
        self.charCheckBox4 = CheckBox("!@#")
        self.charCheckBoxContainer.addWidget(self.charCheckBox1)
        self.charCheckBoxContainer.addWidget(self.charCheckBox2)
        self.charCheckBoxContainer.addWidget(self.charCheckBox3)
        self.charCheckBoxContainer.addWidget(self.charCheckBox4)

        self.excludeLabel = StrongBodyLabel("排除字符", self)
        self.excludeContainer = QHBoxLayout()
        self.excludeLineEdit = LineEdit()
        # self.excludeLineEdit.setFixedWidth(200)
        self.excludeLineEdit.setText("il1I0oO")
        self.excludeSwitchButton = SwitchButton()
        self.excludeSwitchButton.setOnText("启用")
        self.excludeSwitchButton.setOffText("禁用")
        self.excludeContainer.addWidget(self.excludeLineEdit)
        self.excludeContainer.addWidget(self.excludeSwitchButton)

        self.countLabel = StrongBodyLabel("生成数量（1-20）", self)
        self.lenLabel = StrongBodyLabel("密码长度范围（6-50）", self)
        self.countSpinBox = SpinBox()
        self.countSpinBox.setRange(1, 20)
        self.countSpinBox.setValue(1)
        self.lenLowerBoundSpinBox = CompactSpinBox()
        self.lenLowerBoundSpinBox.setRange(6, 50)
        self.lenLowerBoundSpinBox.setValue(8)
        self.separateLabel = StrongBodyLabel("-", self)
        self.lenUpperBoundSpinBox = CompactSpinBox()
        self.lenUpperBoundSpinBox.setRange(6, 50)
        self.lenUpperBoundSpinBox.setValue(12)

        self.includeLabel = StrongBodyLabel("包含指定字符串（可选）", self)
        self.includeLineEdit = LineEdit()
        self.includeLineEdit.setFixedWidth(200)

        self.generateLabel = StrongBodyLabel("点击生成密码按钮以随机生成密码", self)
        self.generateButton = PrimaryPushButton(FIF.PLAY_SOLID, "生成密码")
        self.separator = HorizontalSeparator()
        self.resultLabel = StrongBodyLabel("生成结果", self)
        self.resultBrowser = TextBrowser()
        self.resultBrowser.setReadOnly(True)
        self.resultBrowser.setMinimumHeight(300)
        self.copyButton = PrimaryPushButton(FIF.COPY, "复制")

        self.strengthLabel = StrongBodyLabel("密码强度", self)
        self.strengthBarLabel = StrongBodyLabel("", self)
        self.strengthBarLabel.hide()
        self.strengthBar = ProgressBar(self)
        self.strengthBar.setFixedHeight(8)
        self.strengthBar.setFixedWidth(320)
        self.strengthBar.setUseAni(False)


        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.setSpacing(20)
        self.hBoxLayout = QHBoxLayout()
        self.hBoxLayout2 = QHBoxLayout()
        self.hBoxLayout3 = QHBoxLayout()
        self.hBoxLayout4 = QHBoxLayout()
        self.hBoxLayout5 = QHBoxLayout()
        self.hBoxLayout6 = QHBoxLayout()
        self.hBoxLayout7 = QHBoxLayout()

        self.hBoxLayout.addWidget(self.charLabel)
        self.hBoxLayout.addLayout(self.charCheckBoxContainer)
        self.vBoxLayout.addLayout(self.hBoxLayout)
        self.hBoxLayout4.addWidget(self.excludeLabel)
        self.hBoxLayout4.addStretch(1)
        self.hBoxLayout4.addLayout(self.excludeContainer)
        self.vBoxLayout.addLayout(self.hBoxLayout4)
        self.hBoxLayout2.addWidget(self.countLabel) 
        self.hBoxLayout2.addWidget(self.countSpinBox)
        self.vBoxLayout.addLayout(self.hBoxLayout2)
        self.hBoxLayout3.addWidget(self.lenLabel)
        self.hBoxLayout3.addStretch(1)
        self.hBoxLayout3.addWidget(self.lenLowerBoundSpinBox)
        self.hBoxLayout3.addWidget(self.separateLabel)
        self.hBoxLayout3.addWidget(self.lenUpperBoundSpinBox)
        self.vBoxLayout.addLayout(self.hBoxLayout3)
        self.hBoxLayout5.addWidget(self.includeLabel)
        self.hBoxLayout5.addWidget(self.includeLineEdit)
        self.vBoxLayout.addLayout(self.hBoxLayout5)
        self.hBoxLayout6.addWidget(self.generateLabel)
        self.hBoxLayout6.addStretch(1)
        self.hBoxLayout6.addWidget(self.generateButton, 0, Qt.AlignRight)
        self.vBoxLayout.addLayout(self.hBoxLayout6)
        self.vBoxLayout.addWidget(self.separator)
        self.vBoxLayout.addWidget(self.resultLabel)
        self.vBoxLayout.addWidget(self.resultBrowser)
        self.hBoxLayout7.addWidget(self.strengthLabel)
        self.hBoxLayout7.addWidget(self.strengthBar)
        self.hBoxLayout7.addWidget(self.strengthBarLabel)
        self.hBoxLayout7.addStretch(1)
        self.hBoxLayout7.addWidget(self.copyButton, 0, Qt.AlignRight)
        self.vBoxLayout.addLayout(self.hBoxLayout7)
        
        self.viewLayout.addLayout(self.vBoxLayout)

        # 信号连接
        self.generateButton.clicked.connect(self.generate_password)
        self.copyButton.clicked.connect(self.copy_password)

    def generate_password(self):
        useABC = self.charCheckBox1.isChecked()
        useabc = self.charCheckBox2.isChecked()
        use123 = self.charCheckBox3.isChecked()
        useSymbols = self.charCheckBox4.isChecked()
        excludeText = self.excludeLineEdit.text()
        isWithExclude = self.excludeSwitchButton.isChecked()
        excludeChars = set(excludeText)
        generateCount = self.countSpinBox.value()
        lowerBound = self.lenLowerBoundSpinBox.value()
        upperBound = self.lenUpperBoundSpinBox.value()
        includeText = self.includeLineEdit.text().split()

        try:
            resultPass = self.__generate_password(useABC, useabc, use123, useSymbols, excludeChars, 
                                            isWithExclude, generateCount, lowerBound, upperBound, 
                                            includeText)
            self.resultBrowser.clear()
            for i, p in enumerate(resultPass):
                self.resultBrowser.append(f"{p}")
            passStrength = self.check_pass_strength(resultPass)
            if passStrength == 2:
                self.strengthBar.setValue(100)
                self.strengthBar.setCustomBarColor("#00FF00", "#00FF00")
                self.strengthBarLabel.setText("强")
                self.strengthBarLabel.show()
            elif passStrength == 1:
                self.strengthBar.setValue(66)
                self.strengthBar.setCustomBarColor("#FFA500", "#FFA500")
                self.strengthBarLabel.setText("中")
                self.strengthBarLabel.show()
            elif passStrength == 0:
                self.strengthBar.setValue(33)
                self.strengthBar.setCustomBarColor("#FF0000", "#FF0000")
                self.strengthBarLabel.setText("弱")
                self.strengthBarLabel.show()

        except ValueError as e:
            if str(e) == "没有有效字符可供生成密码":
                w = InfoBar.error(
                    title="生成失败",
                    content="没有有效字符可供生成密码",
                    orient=Qt.Vertical,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=2000,
                    parent=self.mainWindow
                )
                w.show()
            elif str(e) == "密码长度过小，无法包含给定的字符串":
                w = InfoBar.error(
                    title="生成失败",
                    content="密码长度过小，无法包含给定的字符串",
                    orient=Qt.Vertical,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=2000,
                    parent=self.mainWindow
                )
                w.show()
        
    def __generate_password(self, useABC, useabc, use123, useSymbols, excludeChars, 
                            isWithExclude, generateCount, lowerBound, upperBound, includeText):
        all_chars = []
        if useABC:
            all_chars += list(string.ascii_uppercase)
        if useabc:
            all_chars += list(string.ascii_lowercase)
        if use123:
            all_chars += list(string.digits)
        if useSymbols:
            all_chars += ['@', '#', '$', '%', '&', '*', '+', '-', '=']
        if (isWithExclude):
            all_chars = [c for c in all_chars if c not in excludeChars]
        if not all_chars:
            raise ValueError("没有有效字符可供生成密码")
            return
        if lowerBound > upperBound:
            lowerBound, upperBound = upperBound, lowerBound
        result = []
        totalLen = sum(len(s) for s in includeText)
        lowerBound = max(lowerBound - totalLen, 1)
        upperBound = upperBound - totalLen
        print(lowerBound, upperBound)

        for i in range(generateCount):
            if upperBound < 1:
                raise ValueError("密码长度过小，无法包含给定的字符串")
                return
            base_length = random.randint(lowerBound, upperBound)
            # 保证基本密码长度至少满足某个要求（如果需要，也可以根据includeText中各个字符串长度自行调整）
            random_length = base_length  
            
            # 生成随机字符组成的基本密码
            password_chars = random.choices(all_chars, k=random_length)
            generated = "".join(password_chars)
            
            # 如果需要包含指定字符串，则为每个字符串分别随机生成一个插入位置，并按降序插入
            if includeText:
                insertion_points = []
                for s in includeText:
                    pos = random.randint(0, len(generated))
                    insertion_points.append((pos, s))
                # 按插入位置降序排序，确保后插入的不影响前面的插入位置
                insertion_points.sort(key=lambda x: x[0], reverse=True)
                for pos, s in insertion_points:
                    generated = generated[:pos] + s + generated[pos:]
            result.append(generated)
        return result

    def check_pass_strength(self, passwords):
        """
        根据每个密码的长度和包含的字符种类判断密码强度，
        然后统计所有密码中出现最多的强度类别：
            2 代表 "强"  -> 长度>=12 且至少包含3种字符类别
            1 代表 "中"  -> 长度>=8 且至少包含2种字符类别
            0 代表 "弱"  -> 其他情况
        如果没有密码，返回 -1
        """
        if not passwords:
            return -1

        ratings = []
        for password in passwords:
            length = len(password)
            categories = 0
            if any(c.isupper() for c in password):
                categories += 1
            if any(c.islower() for c in password):
                categories += 1
            if any(c.isdigit() for c in password):
                categories += 1
            # 根据生成密码时定义的符号列表判断符号
            if any(c in "@#$%&*+-=" for c in password):
                categories += 1

            if length >= 12 and categories >= 3:
                ratings.append(2)
            elif length >= 8 and categories >= 2:
                ratings.append(1)
            else:
                ratings.append(0)

        # 统计哪个评分出现次数最多
        majority_rating = max(set(ratings), key=ratings.count)
        return majority_rating
        
    def copy_password(self):
        self.resultBrowser.selectAll()
        self.resultBrowser.copy()
        cursor = self.resultBrowser.textCursor()
        cursor.clearSelection()
        self.resultBrowser.setTextCursor(cursor)
        w = InfoBar.success(
            title = "复制成功",
            content="密码已成功复制到剪贴板",
            orient=Qt.Vertical,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=2000,
            parent=self.mainWindow
        )
        w.show()