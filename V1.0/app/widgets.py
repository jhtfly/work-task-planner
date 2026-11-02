# -*- coding: utf-8 -*-
"""主界面组件"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import math
from app.config import load_config, get_schedule, get_current_season
from app.data import (
    load_data, save_data, add_task, complete_task, uncomplete_task,
    delete_task, update_task, get_pending_tasks, get_completed_tasks_today,
    get_completed_tasks_date_range, get_current_week_dates
)
from app.excel_importer import import_tasks_from_excel

# ========== 颜色主题（从配置加载，支持自定义） ==========
from app.config import get_theme as _load_theme
_theme = _load_theme()
BG_MAIN = _theme.get("theme_bg_main", "#F5F6FA")
BG_WHITE = _theme.get("theme_bg_white", "#FFFFFF")
TEXT_DARK = _theme.get("theme_text_dark", "#2C3E50")
TEXT_GRAY = _theme.get("theme_text_gray", "#7F8C8D")
ACCENT_BLUE = _theme.get("theme_accent", "#3498DB")
ACCENT_GREEN = _theme.get("theme_success", "#27AE60")
ACCENT_RED = _theme.get("theme_danger", "#E74C3C")
ACCENT_ORANGE = _theme.get("theme_warning", "#F39C12")
BORDER = _theme.get("theme_border", "#E0E0E0")
TITLE_BAR = _theme.get("theme_titlebar", "#2C3E50")
HEADER_BG = _theme.get("theme_header_bg", "#ECF0F1")
CLOCK_FACE = "#F0F4F8"
CLOCK_HOUR = TEXT_DARK
CLOCK_MINUTE = "#34495E"
CLOCK_SECOND = ACCENT_RED


class AnalogClock(tk.Canvas):
    """模拟时钟组件"""

    def __init__(self, parent, size=120, **kwargs):
        super().__init__(parent, width=size, height=size,
                         bg=CLOCK_FACE, highlightthickness=0, **kwargs)
        self.size = size
        self.center = size // 2
        self.radius = size // 2 - 8
        self._draw_face()

    def _draw_face(self):
        """绘制表盘"""
        self.delete("all")
        c = self.center
        r = self.radius
        self.create_oval(c - r, c - r, c + r, c + r,
                         outline="#BDC3C7", width=2, fill=CLOCK_FACE)
        # 刻度
        for i in range(60):
            angle = math.radians(i * 6 - 90)
            if i % 5 == 0:
                inner_r = r - 12
                outer_r = r - 2
                width = 2
            else:
                inner_r = r - 6
                outer_r = r - 2
                width = 1
            x1 = c + inner_r * math.cos(angle)
            y1 = c + inner_r * math.sin(angle)
            x2 = c + outer_r * math.cos(angle)
            y2 = c + outer_r * math.sin(angle)
            self.create_line(x1, y1, x2, y2, fill="#7F8C8D", width=width)

    def update_time(self):
        """更新时间显示"""
        now = datetime.now()
        h = now.hour % 12
        m = now.minute
        s = now.second
        c = self.center
        r = self.radius

        self.delete("hands")
        # 时针
        h_angle = math.radians((h + m / 60.0) * 30 - 90)
        hx = c + r * 0.5 * math.cos(h_angle)
        hy = c + r * 0.5 * math.sin(h_angle)
        self.create_line(c, c, hx, hy, fill=CLOCK_HOUR, width=4, tags="hands",
                         capstyle=tk.ROUND)
        # 分针
        m_angle = math.radians((m + s / 60.0) * 6 - 90)
        mx = c + r * 0.7 * math.cos(m_angle)
        my = c + r * 0.7 * math.sin(m_angle)
        self.create_line(c, c, mx, my, fill=CLOCK_MINUTE, width=3, tags="hands",
                         capstyle=tk.ROUND)
        # 秒针
        s_angle = math.radians(s * 6 - 90)
        sx = c + r * 0.8 * math.cos(s_angle)
        sy = c + r * 0.8 * math.sin(s_angle)
        self.create_line(c, c, sx, sy, fill=CLOCK_SECOND, width=1.5, tags="hands",
                         capstyle=tk.ROUND)
        # 中心点
        self.create_oval(c - 4, c - 4, c + 4, c + 4,
                         fill=ACCENT_BLUE, outline=ACCENT_BLUE, tags="hands")


class HeaderWidget(tk.Frame):
    """页面头部：时钟 + 日期时间 + 大号数字倒计时"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_WHITE, **kwargs)
        self.configure(highlightbackground=BORDER, highlightthickness=1)
        self._build()

    def _build(self):
        # 左侧：模拟时钟
        self.clock = AnalogClock(self, size=110)
        self.clock.pack(side=tk.LEFT, padx=(15, 5), pady=10)

        # 中间：日期和时间
        mid_frame = tk.Frame(self, bg=BG_WHITE)
        mid_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.lbl_date = tk.Label(mid_frame, text="加载中...", font=("Microsoft YaHei", 10),
                                 fg=TEXT_GRAY, bg=BG_WHITE)
        self.lbl_date.pack(anchor="w")

        self.lbl_time = tk.Label(mid_frame, text="00:00:00", font=("Microsoft YaHei", 26, "bold"),
                                 fg=TEXT_DARK, bg=BG_WHITE)
        self.lbl_time.pack(anchor="w", pady=(2, 0))

        self.lbl_season = tk.Label(mid_frame, text="", font=("Microsoft YaHei", 9),
                                   fg=TEXT_GRAY, bg=BG_WHITE)
        self.lbl_season.pack(anchor="w")

        # 右侧：单个倒计时卡片（上午/下午自动切换）
        right_frame = tk.Frame(self, bg=BG_WHITE)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.cd_frame = tk.Frame(right_frame, bg=BG_WHITE, highlightbackground=BORDER,
                                 highlightthickness=1)
        self.cd_frame.pack(padx=5, pady=3)

        self.lbl_cd_label = tk.Label(self.cd_frame, text="距下班倒计时",
                                     font=("Microsoft YaHei", 10, "bold"),
                                     fg=TEXT_GRAY, bg=BG_WHITE)
        self.lbl_cd_label.pack(padx=16, pady=(8, 2))

        self.lbl_cd_minutes = tk.Label(self.cd_frame, text="--",
                                       font=("Microsoft YaHei", 24, "bold"),
                                       fg=TEXT_DARK, bg=BG_WHITE)
        self.lbl_cd_minutes.pack(padx=16, pady=(2, 0))

        self.lbl_cd_detail = tk.Label(self.cd_frame, text="",
                                      font=("Microsoft YaHei", 9),
                                      fg=TEXT_GRAY, bg=BG_WHITE)
        self.lbl_cd_detail.pack(padx=16, pady=(0, 8))

    def update(self):
        """每秒更新"""
        now = datetime.now()
        schedule = get_schedule()
        season = get_current_season()
        season_name = "夏季作息" if season == "summer" else "冬季作息"

        # 日期和数字时间
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        self.lbl_date.config(text=now.strftime(f"%Y年%m月%d日 {weekdays[now.weekday()]}"))
        self.lbl_time.config(text=now.strftime("%H:%M:%S"))
        self.lbl_season.config(text=f"{season_name} "
                                     f"({schedule['morning_start']}-{schedule['morning_end']} / "
                                     f"{schedule['afternoon_start']}-{schedule['afternoon_end']})")
        self.clock.update_time()

        # 倒计时：仅在上班时段显示，非工作时间隐藏
        def parse_time(s):
            return datetime.strptime(s, "%H:%M").time()

        morning_start = parse_time(schedule["morning_start"])
        morning_end = parse_time(schedule["morning_end"])
        afternoon_start = parse_time(schedule["afternoon_start"])
        afternoon_end = parse_time(schedule["afternoon_end"])
        now_t = now.time()

        in_morning = morning_start <= now_t <= morning_end
        in_afternoon = afternoon_start <= now_t <= afternoon_end

        if in_morning:
            self.lbl_cd_label.config(text="距上午下班", fg="#E67E22")
            end_dt = datetime.combine(now.date(), morning_end)
            diff_secs = max(0, int((end_dt - now).total_seconds()))
            self._set_countdown(diff_secs, schedule['morning_end'])
            self.cd_frame.pack(padx=5, pady=3)
        elif in_afternoon:
            self.lbl_cd_label.config(text="距下午下班", fg="#2980B9")
            end_dt = datetime.combine(now.date(), afternoon_end)
            diff_secs = max(0, int((end_dt - now).total_seconds()))
            self._set_countdown(diff_secs, schedule['afternoon_end'])
            self.cd_frame.pack(padx=5, pady=3)
        else:
            # 非上班时间，隐藏倒计时
            self.cd_frame.pack_forget()

    def _set_countdown(self, total_seconds, target_time):
        """设置倒计时显示（X小时XX分钟格式，黑色字体）"""
        total_minutes = total_seconds // 60
        hours = total_minutes // 60
        mins = total_minutes % 60

        if hours > 0:
            text = f"{hours}小时{mins}分钟"
        else:
            text = f"{mins}分钟"

        self.lbl_cd_minutes.config(text=text, fg="#2C3E50")
        self.lbl_cd_detail.config(text=f"下班时间 {target_time}")


class ScrollableFrame(tk.Frame):
    """可滚动的Frame容器"""

    def __init__(self, parent, **kwargs):
        outer = tk.Frame(parent, bg=BG_MAIN)
        outer.pack(fill=tk.BOTH, expand=True)
        # 为了让 outer 能正确扩展，先设置它的父容器也扩展
        outer.pack_propagate(False)

        self.canvas = tk.Canvas(outer, bg=BG_MAIN, highlightthickness=0)
        self.v_scrollbar = ttk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)

        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        super().__init__(self.canvas, bg=BG_MAIN, **kwargs)
        self._window_id = self.canvas.create_window((0, 0), window=self, anchor="nw", tags="inner_frame")

        # 内框变化时更新滚动区域
        self.bind("<Configure>", self._on_inner_configure)
        # Canvas大小变化时调整内框宽度
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # 鼠标滚轮
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", _on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

    def _on_inner_configure(self, event):
        """内框尺寸变化时，更新Canvas的scrollregion"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_scroll(self):
        """外部可调用，强制更新滚动区域"""
        self.canvas.after(50, self._update_scrollregion)

    def _update_scrollregion(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Canvas宽度变化时，调整内框宽度匹配Canvas"""
        self.canvas.itemconfig(self._window_id, width=event.width)


class SectionTitle(tk.Frame):
    """分区标题组件"""

    def __init__(self, parent, title, bg=BG_MAIN, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        inner = tk.Frame(self, bg=bg)
        inner.pack(fill=tk.X, padx=20, pady=(15, 10))
        tk.Label(inner, text="▪ " + title,
                 font=("Microsoft YaHei", 13, "bold"),
                 fg=TEXT_DARK, bg=bg).pack(side=tk.LEFT)


class TaskPanel(tk.Frame):
    """今日工作任务面板"""

    def __init__(self, parent, root_app, **kwargs):
        super().__init__(parent, bg=BG_MAIN, **kwargs)
        self.root_app = root_app
        self.task_rows = []  # [(frame, name_var, deadline_var, completed_var, task_id)]
        self._build()

    def _build(self):
        SectionTitle(self, "今日工作任务").pack(fill=tk.X)

        # 按钮栏
        btn_bar = tk.Frame(self, bg=BG_MAIN)
        btn_bar.pack(fill=tk.X, padx=20, pady=(0, 5))
        tk.Button(btn_bar, text="+ 添加任务", command=self._add_manual_task,
                  bg=ACCENT_BLUE, fg="white", font=("Microsoft YaHei", 9),
                  relief=tk.FLAT, padx=12, pady=4,
                  activebackground="#2980B9", activeforeground="white",
                  cursor="hand2").pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(btn_bar, text="从Excel刷新导入", command=self._import_from_excel,
                  bg=ACCENT_GREEN, fg="white", font=("Microsoft YaHei", 9),
                  relief=tk.FLAT, padx=12, pady=4,
                  activebackground="#219A52", activeforeground="white",
                  cursor="hand2").pack(side=tk.LEFT)

        # 统一表格（表头 + 数据行在同一 grid 中，确保对齐）
        self.table_frame = tk.Frame(self, bg=BG_MAIN)
        self.table_frame.pack(fill=tk.X, padx=20, pady=(5, 10))
        self.col_weights = [6, 38, 18, 12, 8]
        hdr_texts = ["序号", "任务名称", "任务时限", "状态", "操作"]
        for j, (text, w) in enumerate(zip(hdr_texts, self.col_weights)):
            self.table_frame.grid_columnconfigure(j, weight=w)
            f = tk.Frame(self.table_frame, bg="#ECF0F1")
            f.grid(row=0, column=j, sticky="nsew")
            f.configure(highlightbackground=BORDER, highlightthickness=1)
            tk.Label(f, text=text, font=("Microsoft YaHei", 9, "bold"),
                     fg=TEXT_DARK, bg="#ECF0F1").pack(padx=5, pady=6)

        # 数据行容器引用（用于 refresh）
        self.data_rows = []  # [(row_index, [cell_frames], task_id)]

    def _add_manual_task(self):
        data = load_data()
        add_task(data, "新任务", "")
        save_data(data)
        self.refresh()

    def _add_and_edit_next(self):
        """创建新任务并刷新后自动进入编辑"""
        data = load_data()
        add_task(data, "新任务", "")
        save_data(data)
        self.refresh()
        self.root_app.refresh_all()
        # 等界面刷新完成后自动编辑最后一个待办任务
        self.after(150, self._start_edit_newest)

    def _start_edit_newest(self):
        """找到最新创建的任务行并触发内联编辑"""
        data = load_data()
        pending = get_pending_tasks(data)
        if not pending:
            return
        newest_id = max(t.get("id", 0) for t in pending)
        for name_frame, name_var, deadline_var, completed_var, tid in self.task_rows:
            if tid == newest_id:
                self._edit_task_name_inline(name_frame, tid, name_var)
                return

    def _import_from_excel(self):
        data = load_data()
        config = load_config()
        new_tasks, msg = import_tasks_from_excel(data, config)
        save_data(data)
        self.refresh()
        self.root_app.refresh_all()
        messagebox.showinfo("Excel导入", msg)

    def _toggle_complete(self, task_id, completed_var):
        data = load_data()
        if completed_var.get():
            complete_task(data, task_id)
        else:
            uncomplete_task(data, task_id)
        save_data(data)
        self.refresh()
        self.root_app.refresh_all()

    def _edit_task(self, task_id, name_var, deadline_var):
        """编辑任务名称和时限"""
        dialog = tk.Toplevel(self)
        dialog.title("编辑任务")
        dialog.geometry("400x180")
        dialog.resizable(False, False)
        dialog.configure(bg=BG_WHITE)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        # 居中
        dialog.update_idletasks()
        x = dialog.winfo_screenwidth() // 2 - 200
        y = dialog.winfo_screenheight() // 2 - 90
        dialog.geometry(f"+{x}+{y}")

        tk.Label(dialog, text="任务名称:", font=("Microsoft YaHei", 10),
                 bg=BG_WHITE).pack(padx=20, pady=(20, 0), anchor="w")
        name_entry = tk.Entry(dialog, font=("Microsoft YaHei", 10), width=45)
        name_entry.insert(0, name_var.get())
        name_entry.pack(padx=20, pady=(3, 5), fill=tk.X)

        tk.Label(dialog, text="任务时限:", font=("Microsoft YaHei", 10),
                 bg=BG_WHITE).pack(padx=20, pady=(5, 0), anchor="w")
        deadline_entry = tk.Entry(dialog, font=("Microsoft YaHei", 10), width=45)
        deadline_entry.insert(0, deadline_var.get())
        deadline_entry.pack(padx=20, pady=(3, 5), fill=tk.X)

        def save_edit():
            data = load_data()
            update_task(data, task_id,
                        name=name_entry.get().strip(),
                        deadline_info=deadline_entry.get().strip())
            save_data(data)
            self.refresh()
            self.root_app.refresh_all()
            dialog.destroy()

        tk.Button(dialog, text="保存", command=save_edit,
                  bg=ACCENT_BLUE, fg="white", font=("Microsoft YaHei", 9),
                  relief=tk.FLAT, padx=20, pady=3, cursor="hand2").pack(pady=12)

    def _delete_task(self, task_id):
        if messagebox.askyesno("确认删除", "确定要删除这个任务吗？"):
            data = load_data()
            delete_task(data, task_id)
            save_data(data)
            self.refresh()
            self.root_app.refresh_all()

    def _edit_task_name_inline(self, lbl_frame, task_id, name_var):
        """点击任务名后切换为输入框进行编辑"""
        finished = [False]
        gi = lbl_frame.grid_info()
        grid_row = gi["row"]

        def do_save():
            """执行保存操作"""
            new_name = entry.get().strip()
            if new_name:
                name_var.set(new_name)
                data = load_data()
                update_task(data, task_id, name=new_name)
                save_data(data)

        def restore_ui():
            """恢复标签显示"""
            try:
                entry_frame.grid_forget()
                entry_frame.destroy()
            except Exception:
                pass
            lbl_frame.grid(row=grid_row, column=1, sticky="nsew")

        def cleanup():
            """移除全局点击绑定"""
            root.unbind("<Button-1>")

        def on_return(event):
            """Enter键：保存并创建下一个任务"""
            if finished[0]:
                return "break"
            finished[0] = True
            do_save()
            cleanup()
            restore_ui()
            self._add_and_edit_next()
            return "break"

        def on_focus_out(event=None):
            """失焦：仅保存"""
            if finished[0]:
                return
            finished[0] = True
            do_save()
            cleanup()
            restore_ui()

        # 隐藏标签框架
        lbl_frame.grid_forget()

        # 创建输入框
        entry_frame = tk.Frame(lbl_frame.master, bg=BG_WHITE)
        entry_frame.grid(row=grid_row, column=1, sticky="nsew")
        entry = tk.Entry(entry_frame, font=("Microsoft YaHei", 10),
                         bg="#FFFDE7", relief=tk.FLAT)
        entry.insert(0, name_var.get())
        entry.pack(fill=tk.X, padx=2, pady=6)
        entry.select_range(0, tk.END)
        entry.focus_set()
        entry.bind("<Return>", on_return)
        entry.bind("<FocusOut>", on_focus_out)

        # 点击程序空白区域自动保存
        root = self.winfo_toplevel()
        def on_root_click(event):
            if finished[0]:
                return
            w = event.widget
            while w is not None:
                if w is entry or w is entry_frame:
                    return  # 点在编辑区域内，忽略
                w = w.master
            on_focus_out()  # 点在外部空白处，触发保存
        root.bind("<Button-1>", on_root_click, add="+")

    def _build_task_row(self, idx, task):
        """构建单行任务（单元格直接放入统一表格 grid，确保与表头对齐）"""
        row = idx  # 表头在第0行，数据从第1行开始
        cells = []

        # 第0列：序号
        f0 = tk.Frame(self.table_frame, bg=BG_WHITE)
        f0.grid(row=row, column=0, sticky="nsew")
        f0.configure(highlightbackground=BORDER, highlightthickness=1)
        tk.Label(f0, text=str(idx), font=("Microsoft YaHei", 10),
                 fg=TEXT_DARK, bg=BG_WHITE).pack(padx=5, pady=8)
        cells.append(f0)

        # 第1列：任务名称（可点击编辑）
        f1 = tk.Frame(self.table_frame, bg=BG_WHITE)
        f1.grid(row=row, column=1, sticky="nsew")
        f1.configure(highlightbackground=BORDER, highlightthickness=1)
        name_var = tk.StringVar(value=task.get("name", ""))
        name_lbl = tk.Label(f1, textvariable=name_var, font=("Microsoft YaHei", 10),
                            fg=TEXT_DARK, bg=BG_WHITE, anchor="w", cursor="hand2")
        name_lbl.pack(padx=5, pady=8, fill=tk.X)
        name_lbl.bind("<Button-1>",
                      lambda e, f=f1, tid=task["id"], nv=name_var:
                      self._edit_task_name_inline(f, tid, nv))
        name_lbl.bind("<Enter>", lambda e, l=name_lbl: l.configure(bg="#FFFDE7"))
        name_lbl.bind("<Leave>", lambda e, l=name_lbl: l.configure(bg=BG_WHITE))
        cells.append(f1)

        # 第2列：任务时限
        f2 = tk.Frame(self.table_frame, bg=BG_WHITE)
        f2.grid(row=row, column=2, sticky="nsew")
        f2.configure(highlightbackground=BORDER, highlightthickness=1)
        deadline_var = tk.StringVar(value=task.get("deadline_info", ""))
        dl_color = TEXT_GRAY if "剩余" in task.get("deadline_info", "") else TEXT_DARK
        tk.Label(f2, textvariable=deadline_var, font=("Microsoft YaHei", 9),
                 fg=dl_color, bg=BG_WHITE).pack(padx=5, pady=8)
        cells.append(f2)

        # 第3列：完成状态
        f3 = tk.Frame(self.table_frame, bg=BG_WHITE)
        f3.grid(row=row, column=3, sticky="nsew")
        f3.configure(highlightbackground=BORDER, highlightthickness=1)
        completed_var = tk.BooleanVar(value=task.get("completed", False))
        cb = tk.Checkbutton(f3, text="已完成", variable=completed_var,
                            font=("Microsoft YaHei", 9), bg=BG_WHITE,
                            command=lambda tid=task["id"], cv=completed_var:
                            self._toggle_complete(tid, cv))
        cb.pack(padx=5, pady=8)
        cells.append(f3)

        # 第4列：操作
        f4 = tk.Frame(self.table_frame, bg=BG_WHITE)
        f4.grid(row=row, column=4, sticky="nsew")
        f4.configure(highlightbackground=BORDER, highlightthickness=1)
        btn_frame = tk.Frame(f4, bg=BG_WHITE)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="编辑", font=("Microsoft YaHei", 8),
                  command=lambda t=task["id"], n=name_var, d=deadline_var:
                  self._edit_task(t, n, d),
                  bg="#ECF0F1", relief=tk.FLAT, padx=6, cursor="hand2").pack(side=tk.LEFT, padx=1)
        tk.Button(btn_frame, text="删除", font=("Microsoft YaHei", 8),
                  command=lambda t=task["id"]: self._delete_task(t),
                  bg="#FADBD8", fg=ACCENT_RED, relief=tk.FLAT, padx=6, cursor="hand2").pack(
            side=tk.LEFT, padx=1)
        cells.append(f4)

        self.data_rows.append((row, cells, task["id"]))
        self.task_rows.append((f1, name_var, deadline_var, completed_var, task["id"]))

    def refresh(self):
        """刷新任务列表：清空数据行，保留表头"""
        for row_idx, cells, tid in self.data_rows:
            for cell in cells:
                if cell.winfo_exists():
                    cell.destroy()
        self.data_rows.clear()
        self.task_rows.clear()

        data = load_data()
        tasks = get_pending_tasks(data)
        if not tasks:
            empty_lbl = tk.Label(self.table_frame, text="暂无待办任务",
                                 font=("Microsoft YaHei", 10), fg=TEXT_GRAY,
                                 bg=BG_MAIN)
            empty_lbl.grid(row=1, column=0, columnspan=5, pady=15)
            self.data_rows.append((1, [empty_lbl], -1))
        else:
            for i, task in enumerate(tasks, 1):
                self._build_task_row(i, task)

    def auto_import_on_startup(self):
        """启动时自动导入Excel任务"""
        config = load_config()
        if not config.get("excel_auto_import", True):
            return
        data = load_data()
        new_tasks, msg = import_tasks_from_excel(data, config)
        if new_tasks:
            save_data(data)


class CompletedPanel(tk.Frame):
    """今日已完成工作任务面板"""

    def __init__(self, parent, root_app, **kwargs):
        super().__init__(parent, bg=BG_MAIN, **kwargs)
        self.root_app = root_app
        self._build()

    def _build(self):
        SectionTitle(self, "今日已完成工作任务").pack(fill=tk.X)

        self.container = tk.Frame(self, bg=BG_MAIN)
        self.container.pack(fill=tk.X, padx=20)

    def refresh(self):
        for w in self.container.winfo_children():
            w.destroy()

        data = load_data()
        tasks = get_completed_tasks_today(data)
        if not tasks:
            tk.Label(self.container, text="暂无已完成任务",
                     font=("Microsoft YaHei", 10), fg=TEXT_GRAY,
                     bg=BG_MAIN).pack(pady=10)
            return

        for i, task in enumerate(tasks, 1):
            row = tk.Frame(self.container, bg=BG_WHITE)
            row.pack(fill=tk.X, pady=1)
            row.configure(highlightbackground="#D5F5E3", highlightthickness=1)

            tk.Label(row, text=f"{i}.", font=("Microsoft YaHei", 10),
                     fg=ACCENT_GREEN, bg=BG_WHITE).pack(side=tk.LEFT, padx=(10, 5), pady=8)
            tk.Label(row, text=task.get("name", ""),
                     font=("Microsoft YaHei", 10, "overstrike"),
                     fg=TEXT_GRAY, bg=BG_WHITE, anchor="w").pack(
                side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=8)
            status_text = f"✓ {task.get('completed_date', '')}"
            if task.get("deadline_info"):
                status_text += f" | {task['deadline_info']}"
            tk.Label(row, text=status_text, font=("Microsoft YaHei", 9),
                     fg=ACCENT_GREEN, bg=BG_WHITE).pack(side=tk.RIGHT, padx=10, pady=8)

            # 撤销完成按钮
            tk.Button(row, text="撤销", font=("Microsoft YaHei", 8),
                      command=lambda t=task["id"]: self._undo_complete(t),
                      bg="#FDEBD0", relief=tk.FLAT, padx=6, cursor="hand2").pack(
                side=tk.RIGHT, padx=5, pady=5)

    def _undo_complete(self, task_id):
        data = load_data()
        uncomplete_task(data, task_id)
        save_data(data)
        self.refresh()
        self.root_app.refresh_all()


class WeeklyReport(tk.Frame):
    """工作周报面板"""

    def __init__(self, parent, root_app, **kwargs):
        super().__init__(parent, bg=BG_MAIN, **kwargs)
        self.root_app = root_app
        self._build()

    def _build(self):
        # 标题行
        title_bar = tk.Frame(self, bg=BG_MAIN)
        title_bar.pack(fill=tk.X, padx=20, pady=(15, 5))

        self.lbl_title = tk.Label(title_bar, text="",
                                  font=("Microsoft YaHei", 13, "bold"),
                                  fg=TEXT_DARK, bg=BG_MAIN)
        self.lbl_title.pack(side=tk.LEFT)

        btn_bar = tk.Frame(title_bar, bg=BG_MAIN)
        btn_bar.pack(side=tk.RIGHT)
        tk.Button(btn_bar, text="一键复制", command=self._copy_report,
                  bg=ACCENT_BLUE, fg="white", font=("Microsoft YaHei", 9),
                  relief=tk.FLAT, padx=12, pady=3, cursor="hand2",
                  activebackground="#2980B9").pack(side=tk.LEFT, padx=3)

        # 内容容器
        self.container = tk.Frame(self, bg=BG_MAIN)
        self.container.pack(fill=tk.X, padx=20, pady=(0, 10))

    def _get_report_text(self):
        """获取周报纯文本：仅标题 + 序号 + 任务名称"""
        cfg = load_config()
        name = cfg.get("person_name", "")
        start_date, end_date = get_current_week_dates()

        sd = datetime.strptime(start_date, "%Y-%m-%d")
        ed = datetime.strptime(end_date, "%Y-%m-%d")
        title = f"{name}{sd.year}年{sd.month}月{sd.day}日-{ed.year}年{ed.month}月{ed.day}日工作周报"

        data = load_data()
        tasks = get_completed_tasks_date_range(data, start_date, end_date)

        lines = [title]
        if not tasks:
            lines.append("（本周暂无已完成任务）")
        else:
            for i, task in enumerate(tasks, 1):
                lines.append(f"{i}. {task['name']}")
        return "\n".join(lines)

    def _copy_report(self):
        text = self._get_report_text()
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("复制成功", "周报内容已复制到剪贴板")

    def refresh(self):
        for w in self.container.winfo_children():
            w.destroy()

        cfg = load_config()
        name = cfg.get("person_name", "")
        start_date, end_date = get_current_week_dates()

        sd = datetime.strptime(start_date, "%Y-%m-%d")
        ed = datetime.strptime(end_date, "%Y-%m-%d")
        title = f"{name}{sd.year}年{sd.month}月{sd.day}日-{ed.year}年{ed.month}月{ed.day}日工作周报"
        self.lbl_title.config(text="▪ " + title)

        data = load_data()
        tasks = get_completed_tasks_date_range(data, start_date, end_date)

        if not tasks:
            tk.Label(self.container, text="（本周暂无已完成任务）",
                     font=("Microsoft YaHei", 10), fg=TEXT_GRAY,
                     bg=BG_MAIN).pack(pady=10)
        else:
            for i, task in enumerate(tasks, 1):
                row = tk.Frame(self.container, bg=BG_WHITE)
                row.pack(fill=tk.X, pady=1)
                row.configure(highlightbackground="#D6EAF8", highlightthickness=1)

                tk.Label(row, text=f"{i}.", font=("Microsoft YaHei", 10),
                         fg=ACCENT_BLUE, bg=BG_WHITE).pack(
                    side=tk.LEFT, padx=(10, 5), pady=8)
                text_str = task.get("name", "")
                if task.get("deadline_info"):
                    text_str += f"  [{task['deadline_info']}]"
                text_str += f"  — {task.get('completed_date', '')}"
                tk.Label(row, text=text_str, font=("Microsoft YaHei", 10),
                         fg=TEXT_DARK, bg=BG_WHITE, anchor="w").pack(
                    side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=8)

                tk.Button(row, text="删除", font=("Microsoft YaHei", 8),
                          command=lambda t=task["id"]: self._delete_from_report(t),
                          bg="#FADBD8", fg=ACCENT_RED, relief=tk.FLAT,
                          padx=6, cursor="hand2").pack(side=tk.RIGHT, padx=8, pady=5)

    def _delete_from_report(self, task_id):
        data = load_data()
        delete_task(data, task_id)
        save_data(data)
        self.refresh()
        self.root_app.refresh_all()


class NotesPanel(tk.Frame):
    """笔记区：自由编辑文本，自动保存，一键复制"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_MAIN, **kwargs)
        self._save_timer = None
        self._build()
        self._load_notes()

    def _build(self):
        # 标题行
        title_bar = tk.Frame(self, bg=BG_MAIN)
        title_bar.pack(fill=tk.X, padx=20, pady=(15, 5))
        tk.Label(title_bar, text="▪ 笔记区",
                 font=("Microsoft YaHei", 13, "bold"),
                 fg=TEXT_DARK, bg=BG_MAIN).pack(side=tk.LEFT)
        tk.Button(title_bar, text="一键复制", command=self._copy_notes,
                  bg=ACCENT_BLUE, fg="white", font=("Microsoft YaHei", 9),
                  relief=tk.FLAT, padx=12, pady=3, cursor="hand2",
                  activebackground="#2980B9").pack(side=tk.RIGHT, padx=3)

        # 编辑区域
        text_container = tk.Frame(self, bg=BG_WHITE)
        text_container.pack(fill=tk.X, padx=20, pady=(0, 15))
        text_container.configure(highlightbackground=BORDER, highlightthickness=1)

        self.text_widget = tk.Text(text_container, font=("Microsoft YaHei", 10),
                                   fg=TEXT_DARK, bg=BG_WHITE, height=8,
                                   wrap=tk.WORD, relief=tk.FLAT,
                                   padx=8, pady=8, undo=True)
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # 输入时自动保存（延迟500ms）
        self.text_widget.bind("<KeyRelease>", self._on_text_change)
        self.text_widget.bind("<<Modified>>", self._on_text_change)

    def _on_text_change(self, event=None):
        """输入后延迟自动保存"""
        if self._save_timer:
            self.after_cancel(self._save_timer)
        self._save_timer = self.after(800, self._auto_save)

    def _auto_save(self):
        """自动保存笔记"""
        from app.data import save_notes
        text = self.text_widget.get("1.0", "end-1c")
        save_notes(text)

    def _load_notes(self):
        """加载笔记"""
        from app.data import load_notes
        text = load_notes()
        if text:
            self.text_widget.insert("1.0", text)

    def _copy_notes(self):
        """复制笔记内容"""
        text = self.text_widget.get("1.0", "end-1c")
        if not text.strip():
            messagebox.showinfo("提示", "笔记区暂无内容")
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("复制成功", "笔记内容已复制到剪贴板")

    def save_now(self):
        """外部调用：立即保存"""
        self._auto_save()
