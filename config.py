# coding:utf-8
from enum import Enum
from qfluentwidgets import QConfig, OptionsConfigItem, OptionsValidator, qconfig

class MyConfig(QConfig):
    """应用程序的配置类"""
    backgroundMode = OptionsConfigItem("MainWindow", "BackgroundMode", "Light", OptionsValidator(["Light", "Dark"]), restart = True)

cfg = MyConfig()
qconfig.load('config/config.json', cfg)