import ctypes
import sys
from qfluentwidgets import (NavigationItemPosition, setTheme, Theme, MSFluentWindow,
                            NavigationAvatarWidget, SubtitleLabel, setFont, FlyoutView,
                            FlyoutAnimationType, HyperlinkButton, Flyout, SplashScreen)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt, QUrl, QPoint, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from SettingInterface import SettingInterface
from HomeInterface import HomeInterface
from toolInterface import ToolInterface
from config import cfg

myappid = 'SafeKey'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class MainWindow(MSFluentWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()
        self.homeInterface = HomeInterface('密码管理', self)
        self.settingInterface = SettingInterface('设置', self)
        self.toolInterface = ToolInterface('随机密码生成器', self)
        self.initNavigation()
        

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页', FIF.HOME_FILL)
        self.addSubInterface(self.toolInterface, FIF.DEVELOPER_TOOLS, '工具')
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
        self.setWindowIcon(QIcon('resource/logo.ico'))
        self.setWindowTitle('SafeKey')
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

    def showFlyout(self):
        view = FlyoutView(
            title = '关于本项目',
            content = '本项目是一个简易密码管理器，使用Python编写，基于PyQt5和PyQt-Fluent-Widgets库开发。',
            isClosable= True,
        )

        githubButton = HyperlinkButton(FIF.LINK, "https://github.com/tingyuPP/SafeKey", "仓库地址")
        githubButton.setFixedWidth(120)
        view.addWidget(githubButton, align=Qt.AlignRight)
        view.widgetLayout.insertSpacing(1, 5)
        view.widgetLayout.addSpacing(5)

        # 调整弹出窗口位置
        window_geometry = self.geometry()
        window_bottom_left = QPoint(window_geometry.left(), window_geometry.bottom() - 50)

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

