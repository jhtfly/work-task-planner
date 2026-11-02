# -*- coding: utf-8 -*-
"""日历组件"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import calendar
from app.data import load_data, delete_task, get_completed_tasks_date_range, \
    get_week_dates_for_date
from app.config import load_config, get_theme

# 颜色（从配置主题加载）
_t = get_theme()
BG_MAIN = _t.get("theme_bg_main", "#F5F6FA")
BG_WHITE = _t.get("theme_bg_white", "#FFFFFF")
TEXT_DARK = _t.get("theme_text_dark", "#2C3E50")
TEXT_GRAY = _t.get("theme_text_gray", "#7F8C8D")
ACCENT_BLUE = _t.get("theme_accent", "#3498DB")
ACCENT_GREEN = _t.get("theme_success", "#27AE60")
ACCENT_RED = _t.get("theme_danger", "#E74C3C")
ACCENT_ORANGE = _t.get("theme_warning", "#F39C12")
BORDER = _t.get("theme_border", "#E0E0E0")


class CalendarWidget(tk.Frame):
    """日历视图组件"""

    def __init__(self, parent, root_app, **kwargs):
        super().__init__(parent, bg=BG_MAIN, **kwargs)
        self.root_app = root_app
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.selected_date = None
        self._build()

    def _build(self):
        # 标题
        title_bar = tk.Frame(self, bg=BG_MAIN)
        title_bar.pack(fill=tk.X, padx=20, pady=(15, 5))

        tk.Label(title_bar, text="▪ 日历视图",
                 font=("Microsoft YaHei", 13, "bold"),
                 fg=TEXT_DARK, bg=BG_MAIN).pack(side=tk.LEFT)

        # 月份导航
        nav_frame = tk.Frame(title_bar, bg=BG_MAIN)
        nav_frame.pack(side=tk.RIGHT)

        tk.Button(nav_frame, text="◀", command=self._prev_month,
                  bg="#ECF0F1", relief=tk.FLAT, font=("Microsoft YaHei", 10),
                  padx=8, cursor="hand2").pack(side=tk.LEFT, padx=1)
        self.lbl_month = tk.Label(nav_frame, text="",
                                  font=("Microsoft YaHei", 11, "bold"),
                                  fg=TEXT_DARK, bg=BG_MAIN, width=14)
        self.lbl_month.pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="▶", command=self._next_month,
                  bg="#ECF0F1", relief=tk.FLAT, font=("Microsoft YaHei", 10),
                  padx=8, cursor="hand2").pack(side=tk.LEFT, padx=1)

        # 日历表格
        self.cal_frame = tk.Frame(self, bg=BG_MAIN)
        self.cal_frame.pack(fill=tk.X, padx=20, pady=(0, 5))

        # 详情面板
        self.detail_frame = tk.Frame(self, bg=BG_MAIN)
        self.detail_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

    def _prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self._render_calendar()

    def _next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self._render_calendar()

    def _render_calendar(self):
        """渲染日历表格"""
        for w in self.cal_frame.winfo_children():
            w.destroy()

        self.lbl_month.config(text=f"{self.current_year}年 {self.current_month}月")

        # 获取当月数据
        data = load_data()
        cal = calendar.Calendar(firstweekday=0)  # Monday first
        month_days = cal.monthdayscalendar(self.current_year, self.current_month)

        # 星期标题
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        for j, wd in enumerate(weekdays):
            lbl = tk.Label(self.cal_frame, text=wd,
                           font=("Microsoft YaHei", 9, "bold"),
                           fg=TEXT_GRAY if j >= 5 else TEXT_DARK,
                           bg=BORDER, width=5, height=1)
            lbl.grid(row=0, column=j, padx=1, pady=1, sticky="nsew")

        today = datetime.now().date()
        self.day_labels = {}

        for i, week in enumerate(month_days):
            for j, day in enumerate(week):
                if day == 0:
                    lbl = tk.Label(self.cal_frame, text="", bg=BG_MAIN,
                                   width=5, height=2)
                    lbl.grid(row=i + 1, column=j, padx=1, pady=1, sticky="nsew")
                    continue

                date_obj = datetime(self.current_year, self.current_month, day).date()
                date_str = date_obj.strftime("%Y-%m-%d")

                # 检查该日期是否有已完成任务
                has_completed = any(
                    t.get("completed_date") == date_str
                    for t in data["tasks"] if t.get("completed")
                )

                bg_color = BG_WHITE
                fg_color = TEXT_DARK
                if date_obj == today:
                    bg_color = "#D4E6F1"
                    fg_color = ACCENT_BLUE
                elif j >= 5:  # Weekend
                    bg_color = "#FDF2F2"
                    fg_color = TEXT_GRAY
                if has_completed:
                    bg_color = "#D5F5E3"
                    fg_color = ACCENT_GREEN

                lbl = tk.Label(self.cal_frame, text=str(day),
                               font=("Microsoft YaHei", 9),
                               fg=fg_color, bg=bg_color,
                               width=5, height=2, cursor="hand2",
                               relief=tk.FLAT)
                lbl.grid(row=i + 1, column=j, padx=1, pady=1, sticky="nsew")
                lbl.bind("<Button-1>",
                         lambda e, d=date_obj: self._on_date_click(d))
                # Hover effect
                lbl.bind("<Enter>",
                         lambda e, l=lbl, bg=bg_color:
                         l.configure(bg="#EBF5FB" if bg != "#D4E6F1" else bg))
                lbl.bind("<Leave>",
                         lambda e, l=lbl, bg=bg_color:
                         l.configure(bg=bg))
                self.day_labels[date_obj] = lbl

        # 等分布局
        for j in range(7):
            self.cal_frame.grid_columnconfigure(j, weight=1)

    def _on_date_click(self, date_obj):
        """点击日期显示当日及当周已完成任务"""
        self.selected_date = date_obj
        self._show_detail(date_obj)

        # 高亮选中日期
        for d, lbl in self.day_labels.items():
            if d == date_obj:
                lbl.configure(bg="#3498DB", fg="white")
            else:
                today = datetime.now().date()
                date_str = d.strftime("%Y-%m-%d")
                data = load_data()
                has_completed = any(
                    t.get("completed_date") == date_str
                    for t in data["tasks"] if t.get("completed")
                )
                if d == today:
                    lbl.configure(bg="#D4E6F1", fg=ACCENT_BLUE)
                elif d.weekday() >= 5:
                    lbl.configure(bg="#FDF2F2", fg=TEXT_GRAY)
                elif has_completed:
                    lbl.configure(bg="#D5F5E3", fg=ACCENT_GREEN)
                else:
                    lbl.configure(bg=BG_WHITE, fg=TEXT_DARK)

    def _show_detail(self, date_obj):
        """显示选中日期及当周的已完成任务"""
        for w in self.detail_frame.winfo_children():
            w.destroy()

        date_str = date_obj.strftime("%Y-%m-%d")
        week_start, week_end = get_week_dates_for_date(date_obj)

        sd_dt = datetime.strptime(week_start, "%Y-%m-%d")
        ed_dt = datetime.strptime(week_end, "%Y-%m-%d")

        # 标题栏
        cfg = load_config()
        name = cfg.get("person_name", "")
        title_text = (f"▪ {name} {sd_dt.year}年{sd_dt.month}月{sd_dt.day}日"
                      f"-{ed_dt.year}年{ed_dt.month}月{ed_dt.day}日 工作周报")

        title_frame = tk.Frame(self.detail_frame, bg=BG_MAIN)
        title_frame.pack(fill=tk.X, padx=0, pady=(10, 5))

        tk.Label(title_frame, text=title_text,
                 font=("Microsoft YaHei", 11, "bold"),
                 fg=TEXT_DARK, bg=BG_MAIN).pack(side=tk.LEFT)

        # 当日任务
        sub_frame = tk.Frame(self.detail_frame, bg=BG_WHITE)
        sub_frame.pack(fill=tk.X, padx=0, pady=2)
        sub_frame.configure(highlightbackground=BORDER, highlightthickness=1)

        data = load_data()
        day_tasks = get_completed_tasks_date_range(data, date_str, date_str)
        week_tasks = get_completed_tasks_date_range(data, week_start, week_end)

        # 保存用于复制
        self._current_title = title_text.replace("▪ ", "")
        self._current_day_tasks = day_tasks
        self._current_week_tasks = week_tasks

        # 当日任务显示
        day_header = tk.Frame(sub_frame, bg=BG_WHITE)
        day_header.pack(fill=tk.X, padx=12, pady=(8, 5))
        tk.Label(day_header, text=f"📅 {date_obj.month}月{date_obj.day}日 已完成:",
                 font=("Microsoft YaHei", 10, "bold"),
                 fg=ACCENT_BLUE, bg=BG_WHITE).pack(side=tk.LEFT)
        tk.Button(day_header, text="一键复制", command=self._copy_day_tasks,
                  bg=ACCENT_BLUE, fg="white", font=("Microsoft YaHei", 8),
                  relief=tk.FLAT, padx=8, pady=1, cursor="hand2",
                  activebackground="#2980B9").pack(side=tk.RIGHT)

        if not day_tasks:
            tk.Label(sub_frame, text="  无已完成任务",
                     font=("Microsoft YaHei", 9),
                     fg=TEXT_GRAY, bg=BG_WHITE).pack(
                anchor="w", padx=12, pady=(0, 8))
        else:
            for i, task in enumerate(day_tasks, 1):
                text_str = f"  {i}. {task['name']}"
                if task.get("deadline_info"):
                    text_str += f" [{task['deadline_info']}]"
                tk.Label(sub_frame, text=text_str,
                         font=("Microsoft YaHei", 9),
                         fg=TEXT_DARK, bg=BG_WHITE).pack(
                    anchor="w", padx=12, pady=2)
            tk.Label(sub_frame, text="", bg=BG_WHITE).pack()  # spacing

        # 本周任务
        week_frame = tk.Frame(self.detail_frame, bg=BG_WHITE)
        week_frame.pack(fill=tk.X, padx=0, pady=2)
        week_frame.configure(highlightbackground=BORDER, highlightthickness=1)

        week_header = tk.Frame(week_frame, bg=BG_WHITE)
        week_header.pack(fill=tk.X, padx=12, pady=(8, 5))
        tk.Label(week_header, text="📋 本周已完成:",
                 font=("Microsoft YaHei", 10, "bold"),
                 fg=ACCENT_GREEN, bg=BG_WHITE).pack(side=tk.LEFT)
        tk.Button(week_header, text="一键复制", command=self._copy_week_tasks,
                  bg=ACCENT_GREEN, fg="white", font=("Microsoft YaHei", 8),
                  relief=tk.FLAT, padx=8, pady=1, cursor="hand2",
                  activebackground="#219A52").pack(side=tk.RIGHT)

        if not week_tasks:
            tk.Label(week_frame, text="  无已完成任务",
                     font=("Microsoft YaHei", 9),
                     fg=TEXT_GRAY, bg=BG_WHITE).pack(
                anchor="w", padx=12, pady=(0, 8))
        else:
            # 按日期分组
            from collections import defaultdict
            grouped = defaultdict(list)
            for t in week_tasks:
                grouped[t.get("completed_date", "")].append(t)

            for d in sorted(grouped.keys()):
                dt = datetime.strptime(d, "%Y-%m-%d")
                tk.Label(week_frame,
                         text=f"  {dt.month}月{dt.day}日 ({['一','二','三','四','五','六','日'][dt.weekday()]}):",
                         font=("Microsoft YaHei", 9, "bold"),
                         fg=ACCENT_BLUE, bg=BG_WHITE).pack(
                    anchor="w", padx=12, pady=(5, 2))
                for i, task in enumerate(grouped[d], 1):
                    text_str = f"    {i}. {task['name']}"
                    if task.get("deadline_info"):
                        text_str += f" [{task['deadline_info']}]"
                    tk.Label(week_frame, text=text_str,
                             font=("Microsoft YaHei", 9),
                             fg=TEXT_DARK, bg=BG_WHITE).pack(
                        anchor="w", padx=12, pady=1)
            tk.Label(week_frame, text="", bg=BG_WHITE).pack()

    def _copy_day_tasks(self):
        """复制当日任务清单（仅标题+序号+任务名）"""
        if not hasattr(self, '_current_title') or not self._current_title:
            messagebox.showinfo("提示", "请先点击日历中的某个日期")
            return
        lines = [self._current_title, "", "【当日已完成】"]
        day_tasks = self._current_day_tasks
        if not day_tasks:
            lines.append("  无已完成任务")
        else:
            for i, task in enumerate(day_tasks, 1):
                lines.append(f"  {i}. {task['name']}")
        self.clipboard_clear()
        self.clipboard_append("\n".join(lines))
        messagebox.showinfo("复制成功", "当日任务清单已复制到剪贴板")

    def _copy_week_tasks(self):
        """复制本周任务清单（仅标题+序号+任务名）"""
        if not hasattr(self, '_current_title') or not self._current_title:
            messagebox.showinfo("提示", "请先点击日历中的某个日期")
            return
        lines = [self._current_title, "", "【本周已完成】"]
        week_tasks = self._current_week_tasks
        if not week_tasks:
            lines.append("  无已完成任务")
        else:
            for i, task in enumerate(week_tasks, 1):
                lines.append(f"  {i}. {task['name']}")
        self.clipboard_clear()
        self.clipboard_append("\n".join(lines))
        messagebox.showinfo("复制成功", "本周任务清单已复制到剪贴板")

    def refresh(self):
        self._render_calendar()
        if self.selected_date:
            self._show_detail(self.selected_date)
