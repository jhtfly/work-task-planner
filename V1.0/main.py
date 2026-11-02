# -*- coding: utf-8 -*-
"""
工作任务清单小程序 - 主入口
"""
import tkinter as tk
from tkinter import messagebox
import os
import sys
import ctypes
from datetime import datetime

# ── DPI 感知：提高高分辨率屏幕上的字体清晰度 ──
try:
    # Windows 10 1703+
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        # Windows 8.1
        ctypes.windll.shcore.SetProcessDpiAwareness(0)
    except Exception:
        try:
            # Windows 7/Vista
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# 确保程序目录下的app模块可以被导入
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

from app.config import load_config, APP_DIR, BACKUP_DIR, TASK_DIR
from app.data import load_data, save_data, backup_to_txt
from app.widgets import (
    BG_MAIN, TITLE_BAR, HeaderWidget, ScrollableFrame, TaskPanel,
    CompletedPanel, WeeklyReport, NotesPanel
)
from app.calendar_widget import CalendarWidget
from app.settings import SettingsDialog


class WorkApp:
    """主应用程序"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("工作任务清单")
        self.root.geometry("900x800")
        self.root.minsize(780, 650)
        self.root.configure(bg=BG_MAIN)

        # 设置图标
        try:
            # 优先从 _MEIPASS 加载（PyInstaller 打包后）
            base = sys._MEIPASS if getattr(sys, 'frozen', False) else APP_DIR
            icon_path = os.path.join(base, "图标.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

        # 居中显示
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w = 900
        h = 800
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self._build_ui()
        self._auto_import_on_startup()
        self.refresh_all()
        self._start_clock()

        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        """构建界面"""
        # 标题栏
        title_bar = tk.Frame(self.root, bg=TITLE_BAR, height=40)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)

        tk.Label(title_bar, text="📋 工作任务清单",
                 font=("Microsoft YaHei", 12, "bold"),
                 fg="white", bg=TITLE_BAR).pack(side=tk.LEFT, padx=15, pady=8)

        tk.Button(title_bar, text="设置", command=self._open_settings,
                  font=("Microsoft YaHei", 9),
                  fg="white", bg=TITLE_BAR, relief=tk.FLAT,
                  padx=15, pady=3, cursor="hand2",
                  activebackground="#4A6984").pack(side=tk.RIGHT, padx=10, pady=6)

        # 可滚动主内容区（ScrollableFrame 内部已处理 pack，此处不应再次 pack）
        self.scroll = ScrollableFrame(self.root)

        # 头部（时钟）
        self.header = HeaderWidget(self.scroll)
        self.header.pack(fill=tk.X, padx=15, pady=(10, 5))

        # 今日工作任务
        self.task_panel = TaskPanel(self.scroll, self)
        self.task_panel.pack(fill=tk.X, padx=0, pady=0)

        # 已完成
        self.completed_panel = CompletedPanel(self.scroll, self)
        self.completed_panel.pack(fill=tk.X, padx=0, pady=0)

        # 周报
        self.weekly_report = WeeklyReport(self.scroll, self)
        self.weekly_report.pack(fill=tk.X, padx=0, pady=0)

        # 日历
        self.calendar = CalendarWidget(self.scroll, self)
        self.calendar.pack(fill=tk.X, padx=0, pady=0)

        # 笔记区
        self.notes_panel = NotesPanel(self.scroll)
        self.notes_panel.pack(fill=tk.X, padx=0, pady=0)

    def _auto_import_on_startup(self):
        """启动自动导入"""
        try:
            self.task_panel.auto_import_on_startup()
        except Exception as e:
            # 静默失败，不影响启动
            pass

    def refresh_all(self):
        """刷新所有面板"""
        self.task_panel.refresh()
        self.completed_panel.refresh()
        self.weekly_report.refresh()
        self.calendar.refresh()
        # 确保滚动区域覆盖所有内容
        self.root.after(200, lambda: self.scroll.update_scroll())

    def _start_clock(self):
        """启动时钟更新循环"""
        def tick():
            try:
                self.header.update()
            except Exception:
                pass
            self.root.after(1000, tick)
        tick()

    def _open_settings(self):
        """打开设置对话框"""
        SettingsDialog(self.root, self)

    def _on_close(self):
        """关闭时自动备份并退出"""
        try:
            data = load_data()
            save_data(data)
            backup_to_txt(data, f"清单备份_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            # 保存笔记
            self.notes_panel.save_now()
        except Exception:
            pass
        self.root.destroy()


def main():
    # 确保必要文件夹存在
    for d in [BACKUP_DIR, TASK_DIR]:
        os.makedirs(d, exist_ok=True)

    app = WorkApp()
    app.root.mainloop()


if __name__ == "__main__":
    main()
