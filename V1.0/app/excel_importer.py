# -*- coding: utf-8 -*-
"""Excel任务导入模块"""
import os
from app.config import TASK_DIR


def column_letter_to_index(letter):
    """将Excel列字母转换为0-based索引：A->0, B->1, ..., Z->25, AA->26"""
    letter = letter.upper().strip()
    result = 0
    for ch in letter:
        if 'A' <= ch <= 'Z':
            result = result * 26 + (ord(ch) - ord('A') + 1)
    return result - 1


def find_excel_file():
    """在'工作任务'文件夹中查找首个Excel文件"""
    if not os.path.exists(TASK_DIR):
        return None
    excel_exts = ('.xlsx', '.xls', '.xlsm')
    try:
        files = os.listdir(TASK_DIR)
        for f in sorted(files):
            if f.lower().endswith(excel_exts) and not f.startswith('~$'):
                return os.path.join(TASK_DIR, f)
    except Exception:
        pass
    return None


def import_tasks_from_excel(data, config, parent_widget=None):
    """
    从Excel导入任务
    返回: (新任务列表, 消息)
    """
    excel_path = find_excel_file()
    if not excel_path:
        return [], "未在「工作任务」文件夹中找到Excel文件"

    sheet_name = config.get("excel_sheet_name", "工作任务清单")
    task_col = config.get("excel_task_column", "D")
    deadline_col = config.get("excel_deadline_column", "O")
    threshold = config.get("auto_import_threshold_days", 7)
    dedup_days = config.get("import_dedup_days", 30)

    task_col_idx = column_letter_to_index(task_col)
    deadline_col_idx = column_letter_to_index(deadline_col)
    max_col = max(task_col_idx, deadline_col_idx) + 1

    try:
        import openpyxl
    except ImportError:
        return [], "缺少openpyxl库，请安装: pip install openpyxl"

    try:
        wb = openpyxl.load_workbook(excel_path, data_only=True, read_only=True)
    except Exception as e:
        return [], f"无法打开Excel文件: {e}"

    if sheet_name not in wb.sheetnames:
        wb.close()
        return [], f"找不到工作表「{sheet_name}」，可用工作表: {', '.join(wb.sheetnames)}"

    ws = wb[sheet_name]
    new_tasks = []
    skipped = 0

    for row_idx, row in enumerate(ws.iter_rows(min_row=2, max_col=max_col, values_only=True), start=2):
        task_name = None
        days_left = None

        if task_col_idx < len(row):
            task_name = row[task_col_idx]
        if deadline_col_idx < len(row):
            raw_val = row[deadline_col_idx]
            if raw_val is not None:
                try:
                    days_left = int(float(str(raw_val)))
                except (ValueError, TypeError):
                    pass

        if not task_name or str(task_name).strip() == "":
            continue

        task_name = str(task_name).strip()

        # 检查导入去重
        from app.data import is_task_imported_recently, mark_task_imported
        if is_task_imported_recently(data, task_name, dedup_days):
            skipped += 1
            continue

        # 检查天数阈值：仅导入 0 <= 剩余天数 < threshold 的任务
        # 已过期（负数）或无截止日期的任务不自动导入
        if days_left is None or days_left < 0 or days_left >= threshold:
            skipped += 1
            continue

        # 添加任务（此时 days_left 一定不为 None 且 < threshold）
        deadline_info = f"剩余{days_left}天"
        from app.data import add_task
        task = add_task(data, task_name, deadline_info, days_left, source="excel")
        mark_task_imported(data, task_name)
        new_tasks.append(task)

    wb.close()

    msg = f"从「{os.path.basename(excel_path)}」{sheet_name}工作表导入 {len(new_tasks)} 个新任务"
    if skipped > 0:
        msg += f"（跳过 {skipped} 个）"
    return new_tasks, msg
