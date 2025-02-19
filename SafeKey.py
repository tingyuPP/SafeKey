import ctypes
import sys
from qfluentwidgets import (NavigationItemPosition, setTheme, Theme, MSFluentWindow,
                            NavigationAvatarWidget, qrouter, SubtitleLabel, setFont, FlyoutView,
                            FlyoutAnimationType, HyperlinkButton, Flyout,)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt, QUrl, QPoint
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout
from SettingInterface import SettingInterface
from config import cfg

myappid = 'SafeKey'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))

class MainWindow(MSFluentWindow):

    def __init__(self):
        super().__init__()

        # 设置主题
        if cfg.backgroundMode.value == 'Dark':
            setTheme(Theme.DARK)
        else:
            setTheme(Theme.LIGHT)
            
        # create sub interface
        self.homeInterface = Widget('Home Interface', self)
        self.settingInterface = SettingInterface('设置', self)

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页', FIF.HOME_FILL)
        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置')

        # 添加自定义导航组件
        self.navigationInterface.addItem(
            routeKey='About',
            icon=FIF.PEOPLE,
            text='关于',
            onClick=self.showFlyout,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        self.navigationInterface.setCurrentItem(self.homeInterface.objectName())

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('SafeKey')

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

    def showFlyout(self):
        view = FlyoutView(
            title = '关于本项目',
            content = '本项目是一个密码管理器，用于存储用户的网站账号和密码，以及其他重要信息。',
            image = 'image/hua.jpg',
            isClosable= True,
        )

        githubButton = HyperlinkButton(FIF.LINK, "https://github.com/tingyuPP/SafeKey", "仓库地址")
        githubButton.setFixedWidth(120)
        view.addWidget(githubButton, align=Qt.AlignRight)

        view.widgetLayout.insertSpacing(1, 5)
        view.widgetLayout.addSpacing(5)

        window_geometry = self.geometry()
        window_bottom_left = QPoint(window_geometry.left(), window_geometry.bottom() - 400)

        # 显示弹出窗口
        w = Flyout.make(view, window_bottom_left, self)
        view.closed.connect(w.close)


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()

