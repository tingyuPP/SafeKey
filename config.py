# coding:utf-8
from enum import Enum
from qfluentwidgets import QConfig, OptionsConfigItem, OptionsValidator, qconfig, ConfigItem, FolderValidator
import os

class MyConfig(QConfig):
    """应用程序的配置类"""
    exportDir = ConfigItem("MainWindow", "ExportDir", "",validator = FolderValidator(),restart = False)
    importSetting = OptionsConfigItem("MainWindow", "ImportSetting", "Override", OptionsValidator(["Override", "Skip"]),restart = False)

cfg = MyConfig()
qconfig.load('config/config.json', cfg)

if not cfg.get(cfg.exportDir):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    cfg.set(cfg.exportDir, project_root)