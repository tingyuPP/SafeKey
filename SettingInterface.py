from PyQt5.QtWidgets import QFrame, QWidget
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QSizePolicy
from qfluentwidgets import SubtitleLabel, setFont, OptionsSettingCard, setTheme, Theme
from config import cfg

class SettingInterface(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(20)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # 为 label 设置左边距
        self.label.setContentsMargins(20, 0, 0, 0)
        self.vBoxLayout.addWidget(self.label, 0, Qt.AlignLeft | Qt.AlignTop)
        self.setObjectName(text.replace(' ', '-'))

        self.backgroundCard = OptionsSettingCard(
            cfg.backgroundMode,
            FIF.BRUSH,
            self.tr('更改主题格式'),
            self.tr("改变应用程序的主题格式"),
            texts=[
                self.tr('明亮'), self.tr('暗黑'),
            ],
        )
        self.backgroundCard.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.vBoxLayout.addWidget(self.backgroundCard, 1, Qt.AlignTop)

        # 设置布局边距
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)

        # 连接 optionChanged 信号到槽函数
        self.backgroundCard.optionChanged.connect(self.onOptionChanged)

    def onOptionChanged(self, item):
        """
        当选项改变时触发，根据用户选择的选项切换主题
        """
        # 获取当前选中的选项
        selected_option = item.value

        # 根据选项设置主题
        if selected_option == 'Light':
            setTheme(Theme.LIGHT)
        elif selected_option == 'Dark':
            setTheme(Theme.DARK)
        else:
            # 默认使用浅色主题
            setTheme(Theme.LIGHT)