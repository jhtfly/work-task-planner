# -*- coding: utf-8 -*-
"""配置管理模块"""
import json
import os
import sys
from datetime import datetime


def get_app_dir():
    """获取应用程序根目录（exe运行或源码运行时都能正确获取）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


APP_DIR = get_app_dir()
CONFIG_FILE = os.path.join(APP_DIR, 'config.json')
DATA_FILE = os.path.join(APP_DIR, 'data.json')
BACKUP_DIR = os.path.join(APP_DIR, '清单备份')
TASK_DIR = os.path.join(APP_DIR, '工作任务')

DEFAULT_CONFIG = {
    "summer_morning_start": "08:30",
    "summer_morning_end": "11:30",
    "summer_afternoon_start": "14:00",
    "summer_afternoon_end": "17:30",
    "winter_morning_start": "08:30",
    "winter_morning_end": "11:30",
    "winter_afternoon_start": "14:30",
    "winter_afternoon_end": "17:00",
    "summer_months": [5, 6, 7, 8, 9],
    "person_name": "张三",
    "excel_auto_import": True,
    "excel_sheet_name": "工作任务清单",
    "excel_task_column": "D",
    "excel_deadline_column": "O",
    "auto_import_threshold_days": 7,
    "import_dedup_days": 30,
    # 主题颜色
    "theme_bg_main": "#F5F6FA",
    "theme_bg_white": "#FFFFFF",
    "theme_text_dark": "#2C3E50",
    "theme_text_gray": "#7F8C8D",
    "theme_accent": "#3498DB",
    "theme_success": "#27AE60",
    "theme_danger": "#E74C3C",
    "theme_warning": "#F39C12",
    "theme_border": "#E0E0E0",
    "theme_titlebar": "#2C3E50",
    "theme_header_bg": "#ECF0F1",
}

DEFAULT_THEME = {k: v for k, v in DEFAULT_CONFIG.items() if k.startswith("theme_")}


def get_theme():
    """获取当前主题颜色"""
    cfg = load_config()
    theme = {}
    for k, v in DEFAULT_THEME.items():
        theme[k] = cfg.get(k, v)
    return theme


def save_theme(theme_colors):
    """保存主题颜色"""
    cfg = load_config()
    for k, v in theme_colors.items():
        if k.startswith("theme_"):
            cfg[k] = v
    save_config(cfg)


def load_config():
    """加载配置，合并默认值"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg
        except Exception:
            return dict(DEFAULT_CONFIG)
    return dict(DEFAULT_CONFIG)


def save_config(cfg):
    """保存配置到文件"""
    os.makedirs(APP_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def reset_all():
    """重置所有数据和配置"""
    for f in [CONFIG_FILE, DATA_FILE]:
        if os.path.exists(f):
            os.remove(f)


def get_current_season():
    """根据当前月份判断夏季/冬季"""
    cfg = load_config()
    month = datetime.now().month
    if month in cfg.get("summer_months", [5, 6, 7, 8, 9]):
        return "summer"
    return "winter"


def get_schedule():
    """获取当前作息时间表"""
    cfg = load_config()
    season = get_current_season()
    return {
        "morning_start": cfg[f"{season}_morning_start"],
        "morning_end": cfg[f"{season}_morning_end"],
        "afternoon_start": cfg[f"{season}_afternoon_start"],
        "afternoon_end": cfg[f"{season}_afternoon_end"],
    }
