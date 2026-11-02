# -*- coding: utf-8 -*-
"""设置对话框"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
from datetime import datetime
import os
from app.config import load_config, save_config, reset_all, APP_DIR, BACKUP_DIR, DEFAULT_THEME
from app.data import load_data, backup_to_txt

BG_WHITE = "#FFFFFF"
BG_MAIN = "#F5F6FA"
TEXT_DARK = "#2C3E50"
TEXT_GRAY = "#7F8C8D"
ACCENT_BLUE = "#3498DB"
ACCENT_GREEN = "#27AE60"
ACCENT_RED = "#E74C3C"
BORDER = "#E0E0E0"


class SettingsDialog(tk.Toplevel):
    """设置对话框"""

    def __init__(self, parent, root_app):
        super().__init__(parent)
        self.root_app = root_app
        self.title("设置")
        self.geometry("580x720")
        self.resizable(False, False)
        self.configure(bg=BG_MAIN)
        self.transient(parent)
        self.grab_set()

        # 居中
        self.update_idletasks()
        x = self.winfo_screenwidth() // 2 - 290
        y = self.winfo_screenheight() // 2 - 340
        self.geometry(f"+{x}+{y}")

        self.config_data = load_config()
        self._build()

    def _section_label(self, parent, text):
        tk.Label(parent, text=text, font=("Microsoft YaHei", 11, "bold"),
                 fg=TEXT_DARK, bg=BG_MAIN).pack(anchor="w", pady=(15, 5))

    def _entry_row(self, parent, label, var, width=10):
        row = tk.Frame(parent, bg=BG_MAIN)
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text=label, font=("Microsoft YaHei", 10),
                 fg=TEXT_DARK, bg=BG_MAIN, width=22, anchor="w").pack(side=tk.LEFT)
        entry = tk.Entry(row, textvariable=var, font=("Microsoft YaHei", 10),
                         width=width, justify="center")
        entry.pack(side=tk.LEFT, padx=5)
        return entry

    def _build(self):
        # 使用Notebook分为多个tab
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ===== Tab 1: 作息时间 =====
        tab1 = tk.Frame(notebook, bg=BG_MAIN)
        notebook.add(tab1, text="  作息时间  ")

        self._section_label(tab1, "夏季作息时间")
        self.sv_morning_start = tk.StringVar(value=self.config_data.get("summer_morning_start", "08:30"))
        self.sv_morning_end = tk.StringVar(value=self.config_data.get("summer_morning_end", "11:30"))
        self.sv_afternoon_start = tk.StringVar(value=self.config_data.get("summer_afternoon_start", "14:00"))
        self.sv_afternoon_end = tk.StringVar(value=self.config_data.get("summer_afternoon_end", "17:00"))

        f1 = tk.Frame(tab1, bg=BG_MAIN)
        f1.pack(fill=tk.X, padx=20)
        self._entry_row(f1, "上午上班时间:", self.sv_morning_start)
        self._entry_row(f1, "上午下班时间:", self.sv_morning_end)
        self._entry_row(f1, "下午上班时间:", self.sv_afternoon_start)
        self._entry_row(f1, "下午下班时间:", self.sv_afternoon_end)

        self._section_label(tab1, "冬季作息时间")
        self.w_morning_start = tk.StringVar(value=self.config_data.get("winter_morning_start", "08:30"))
        self.w_morning_end = tk.StringVar(value=self.config_data.get("winter_morning_end", "11:30"))
        self.w_afternoon_start = tk.StringVar(value=self.config_data.get("winter_afternoon_start", "14:30"))
        self.w_afternoon_end = tk.StringVar(value=self.config_data.get("winter_afternoon_end", "17:30"))

        f2 = tk.Frame(tab1, bg=BG_MAIN)
        f2.pack(fill=tk.X, padx=20)
        self._entry_row(f2, "上午上班时间:", self.w_morning_start)
        self._entry_row(f2, "上午下班时间:", self.w_morning_end)
        self._entry_row(f2, "下午上班时间:", self.w_afternoon_start)
        self._entry_row(f2, "下午下班时间:", self.w_afternoon_end)

        self._section_label(tab1, "夏季月份范围")
        f3 = tk.Frame(tab1, bg=BG_MAIN)
        f3.pack(fill=tk.X, padx=20)
        summer_default = self.config_data.get("summer_months", [5, 6, 7, 8, 9])
        self.summer_months_var = tk.StringVar(
            value=",".join(str(m) for m in summer_default))
        self._entry_row(f3, "夏季月份 (逗号分隔):", self.summer_months_var, width=20)

        # ===== Tab 2: Excel配置 =====
        tab2 = tk.Frame(notebook, bg=BG_MAIN)
        notebook.add(tab2, text="  Excel导入  ")

        self._section_label(tab2, "Excel导入配置")
        f4 = tk.Frame(tab2, bg=BG_MAIN)
        f4.pack(fill=tk.X, padx=20)

        self.auto_import_var = tk.BooleanVar(
            value=self.config_data.get("excel_auto_import", True))
        tk.Checkbutton(f4, text="启动时自动从Excel导入任务",
                       variable=self.auto_import_var,
                       font=("Microsoft YaHei", 10),
                       bg=BG_MAIN).pack(anchor="w", pady=5)

        self.sheet_var = tk.StringVar(value=self.config_data.get("excel_sheet_name", "工作任务清单"))
        self._entry_row(f4, "工作表名称:", self.sheet_var, width=20)

        self.task_col_var = tk.StringVar(value=self.config_data.get("excel_task_column", "D"))
        self._entry_row(f4, "任务名称列:", self.task_col_var, width=8)

        self.deadline_col_var = tk.StringVar(value=self.config_data.get("excel_deadline_column", "O"))
        self._entry_row(f4, "剩余天数列:", self.deadline_col_var, width=8)

        self.threshold_var = tk.StringVar(
            value=str(self.config_data.get("auto_import_threshold_days", 7)))
        self._entry_row(f4, "导入阈值 (剩余天数<):", self.threshold_var, width=8)

        self.dedup_var = tk.StringVar(
            value=str(self.config_data.get("import_dedup_days", 30)))
        self._entry_row(f4, "去重天数 (N天内不重复导入):", self.dedup_var, width=8)

        tk.Label(f4, text="提示: Excel文件请放入「工作任务」文件夹",
                 font=("Microsoft YaHei", 9), fg=TEXT_GRAY,
                 bg=BG_MAIN).pack(anchor="w", pady=(10, 0))

        # ===== Tab 3: 周报设置 =====
        tab3 = tk.Frame(notebook, bg=BG_MAIN)
        notebook.add(tab3, text="  周报设置  ")

        self._section_label(tab3, "周报署名")
        f5 = tk.Frame(tab3, bg=BG_MAIN)
        f5.pack(fill=tk.X, padx=20)
        self.name_var = tk.StringVar(value=self.config_data.get("person_name", "张三"))
        self._entry_row(f5, "姓名/岗位名称:", self.name_var, width=20)

        # ===== Tab 4: 主题 =====
        tab4 = tk.Frame(notebook, bg=BG_MAIN)
        notebook.add(tab4, text="  主题  ")

        self._section_label(tab4, "自定义主题颜色")
        f8 = tk.Frame(tab4, bg=BG_MAIN)
        f8.pack(fill=tk.X, padx=20)
        tk.Label(f8, text="点击色块打开系统色盘选择颜色，保存后重启生效",
                 font=("Microsoft YaHei", 9), fg=TEXT_GRAY,
                 bg=BG_MAIN).pack(anchor="w", pady=(0, 8))

        self.theme_vars = {}
        self.theme_labels = {}
        theme_names = [
            ("theme_bg_main", "页面背景"),
            ("theme_bg_white", "卡片/表格背景"),
            ("theme_text_dark", "主文字颜色"),
            ("theme_text_gray", "次要文字颜色"),
            ("theme_accent", "主色调 (按钮等)"),
            ("theme_success", "成功色 (完成/绿色)"),
            ("theme_danger", "危险色 (删除/红色)"),
            ("theme_warning", "警告色 (提醒/橙色)"),
            ("theme_border", "边框颜色"),
            ("theme_titlebar", "标题栏背景"),
            ("theme_header_bg", "表头背景"),
        ]

        for key, label in theme_names:
            row_f = tk.Frame(f8, bg=BG_MAIN)
            row_f.pack(fill=tk.X, pady=2)
            tk.Label(row_f, text=label, font=("Microsoft YaHei", 9),
                     fg=TEXT_DARK, bg=BG_MAIN, width=20, anchor="w").pack(side=tk.LEFT)

            current_color = self.config_data.get(key, DEFAULT_THEME.get(key, "#000000"))
            color_var = tk.StringVar(value=current_color)
            self.theme_vars[key] = color_var

            # 色块预览
            swatch = tk.Label(row_f, text="    ", bg=current_color, relief=tk.RIDGE, width=4)
            swatch.pack(side=tk.LEFT, padx=(5, 5))
            self.theme_labels[key] = swatch

            # 颜色代码输入
            entry = tk.Entry(row_f, textvariable=color_var, font=("Consolas", 9), width=10)
            entry.pack(side=tk.LEFT, padx=(0, 5))

            # 选择按钮
            tk.Button(row_f, text="选色",
                      command=lambda k=key, v=color_var, s=swatch: self._pick_color(k, v, s),
                      font=("Microsoft YaHei", 8), bg="#ECF0F1", relief=tk.FLAT,
                      padx=6, cursor="hand2").pack(side=tk.LEFT)

        tk.Button(f8, text="恢复默认主题", command=self._reset_theme,
                  font=("Microsoft YaHei", 9), bg="#FADBD8", fg=ACCENT_RED,
                  relief=tk.FLAT, padx=12, pady=4, cursor="hand2").pack(anchor="w", pady=(10, 0))

        # ===== Tab 5: 备份与重置 =====
        tab5 = tk.Frame(notebook, bg=BG_MAIN)
        notebook.add(tab5, text="  备份与重置  ")

        self._section_label(tab5, "数据备份")
        f6 = tk.Frame(tab5, bg=BG_MAIN)
        f6.pack(fill=tk.X, padx=20)
        tk.Label(f6, text=f"备份文件夹: {BACKUP_DIR}",
                 font=("Microsoft YaHei", 9), fg=TEXT_GRAY,
                 bg=BG_MAIN).pack(anchor="w", pady=5)

        tk.Button(f6, text="  立即备份  ", command=self._manual_backup,
                  bg=ACCENT_GREEN, fg="white", font=("Microsoft YaHei", 10),
                  relief=tk.FLAT, padx=20, pady=6,
                  activebackground="#219A52", cursor="hand2").pack(anchor="w", pady=10)

        self._section_label(tab5, "危险操作")
        f7 = tk.Frame(tab5, bg=BG_MAIN)
        f7.pack(fill=tk.X, padx=20)
        tk.Label(f7, text="软件重置将清除所有数据和配置参数",
                 font=("Microsoft YaHei", 9), fg=ACCENT_RED,
                 bg=BG_MAIN).pack(anchor="w")

        tk.Button(f7, text="  软件重置  ", command=self._reset,
                  bg=ACCENT_RED, fg="white", font=("Microsoft YaHei", 10),
                  relief=tk.FLAT, padx=20, pady=6,
                  activebackground="#CB4335", cursor="hand2").pack(
            anchor="w", pady=10)

        # ===== 底部按钮 =====
        bottom_bar = tk.Frame(self, bg=BG_MAIN)
        bottom_bar.pack(fill=tk.X, padx=20, pady=(10, 15))
        tk.Button(bottom_bar, text="  取消  ", command=self.destroy,
                  font=("Microsoft YaHei", 10),
                  bg="#ECF0F1", relief=tk.FLAT, padx=25, pady=5,
                  cursor="hand2").pack(side=tk.RIGHT, padx=5)
        tk.Button(bottom_bar, text="  保存设置  ", command=self._save,
                  font=("Microsoft YaHei", 10),
                  bg=ACCENT_BLUE, fg="white", relief=tk.FLAT, padx=25, pady=5,
                  activebackground="#2980B9", cursor="hand2").pack(
            side=tk.RIGHT, padx=5)

    def _save(self):
        """保存设置"""
        try:
            summer_months = [int(m.strip()) for m in self.summer_months_var.get().split(",")
                             if m.strip()]
            if not summer_months:
                summer_months = [5, 6, 7, 8, 9]
            threshold = int(self.threshold_var.get())
            dedup = int(self.dedup_var.get())
        except ValueError:
            messagebox.showerror("输入错误", "月份范围和天数值必须为整数")
            return

        self.config_data.update({
            "summer_morning_start": self.sv_morning_start.get(),
            "summer_morning_end": self.sv_morning_end.get(),
            "summer_afternoon_start": self.sv_afternoon_start.get(),
            "summer_afternoon_end": self.sv_afternoon_end.get(),
            "winter_morning_start": self.w_morning_start.get(),
            "winter_morning_end": self.w_morning_end.get(),
            "winter_afternoon_start": self.w_afternoon_start.get(),
            "winter_afternoon_end": self.w_afternoon_end.get(),
            "summer_months": summer_months,
            "excel_auto_import": self.auto_import_var.get(),
            "excel_sheet_name": self.sheet_var.get(),
            "excel_task_column": self.task_col_var.get().upper(),
            "excel_deadline_column": self.deadline_col_var.get().upper(),
            "auto_import_threshold_days": threshold,
            "import_dedup_days": dedup,
            "person_name": self.name_var.get(),
        })
        # 保存主题颜色
        for key, var in self.theme_vars.items():
            self.config_data[key] = var.get()
        save_config(self.config_data)
        messagebox.showinfo("设置已保存", "配置已更新，主题颜色将在下次启动程序时生效")
        self.destroy()
        # 刷新主界面
        if self.root_app:
            self.root_app.refresh_all()

    def _pick_color(self, key, var, swatch):
        """打开系统色盘选择颜色"""
        result = colorchooser.askcolor(color=var.get(), title="选择颜色")
        if result and result[1]:
            var.set(result[1])
            swatch.configure(bg=result[1])

    def _reset_theme(self):
        """恢复默认主题颜色"""
        if not messagebox.askyesno("确认", "确定恢复默认主题颜色吗？"):
            return
        for key, default_val in DEFAULT_THEME.items():
            if key in self.theme_vars:
                self.theme_vars[key].set(default_val)
                self.theme_labels[key].configure(bg=default_val)
        messagebox.showinfo("已恢复", "主题颜色已恢复为默认值，保存后重启生效")

    def _manual_backup(self):
        """手动备份"""
        data = load_data()
        success = backup_to_txt(data)
        if success:
            messagebox.showinfo("备份成功", f"数据已备份到:\n{BACKUP_DIR}")
        else:
            messagebox.showerror("备份失败", "写入备份文件失败，请检查文件夹权限")

    def _reset(self):
        """重置软件"""
        if not messagebox.askyesno("确认重置",
                                   "此操作将清除所有数据和配置参数！\n\n确定要继续吗？",
                                   icon="warning"):
            return
        if messagebox.askyesno("再次确认",
                               "重置后数据无法恢复！\n\n确定要重置吗？",
                               icon="error"):
            reset_all()
            messagebox.showinfo("已重置", "所有数据和配置已清除，程序将关闭。")
            self.destroy()
            if self.root_app:
                self.root_app.master.destroy()
