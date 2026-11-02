# -*- coding: utf-8 -*-
"""任务数据管理模块"""
import json
import os
from datetime import datetime, timedelta
from app.config import DATA_FILE, load_config, BACKUP_DIR


def load_data():
    """加载任务数据"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = {"tasks": [], "imported_records": []}
    else:
        data = {"tasks": [], "imported_records": []}
    if "imported_records" not in data:
        data["imported_records"] = []
    return data


def save_data(data):
    """保存任务数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _next_id(data):
    """生成下一个任务ID"""
    ids = [t.get("id", 0) for t in data["tasks"]]
    return max(ids) + 1 if ids else 1


def add_task(data, name, deadline_info="", deadline_days=None, source="manual"):
    """添加新任务"""
    task = {
        "id": _next_id(data),
        "name": name,
        "deadline_info": deadline_info,
        "deadline_days": deadline_days,
        "completed": False,
        "completed_date": None,
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "source": source,
    }
    data["tasks"].append(task)
    return task


def complete_task(data, task_id):
    """标记任务为已完成"""
    for t in data["tasks"]:
        if t["id"] == task_id and not t["completed"]:
            t["completed"] = True
            t["completed_date"] = datetime.now().strftime("%Y-%m-%d")
            return t
    return None


def uncomplete_task(data, task_id):
    """撤销任务完成状态"""
    for t in data["tasks"]:
        if t["id"] == task_id and t["completed"]:
            t["completed"] = False
            t["completed_date"] = None
            return t
    return None


def delete_task(data, task_id):
    """删除任务"""
    data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]


def update_task(data, task_id, name=None, deadline_info=None):
    """更新任务内容"""
    for t in data["tasks"]:
        if t["id"] == task_id:
            if name is not None:
                t["name"] = name
            if deadline_info is not None:
                t["deadline_info"] = deadline_info
            return t
    return None


def get_pending_tasks(data):
    """获取所有未完成的任务（按ID排序，跨天保留）"""
    tasks = [t for t in data["tasks"] if not t["completed"]]
    tasks.sort(key=lambda t: t.get("id", 0))
    return tasks


def get_completed_tasks_today(data):
    """获取今日已完成的任务（按完成时间排序）"""
    today = datetime.now().strftime("%Y-%m-%d")
    tasks = [t for t in data["tasks"]
             if t["completed"] and t["completed_date"] == today]
    tasks.sort(key=lambda t: t.get("id", 0))
    return tasks


def get_completed_tasks_date_range(data, start_date, end_date):
    """获取指定日期范围内的已完成任务（从旧到新）"""
    result = [t for t in data["tasks"]
              if t["completed"] and t["completed_date"] and start_date <= t["completed_date"] <= end_date]
    result.sort(key=lambda t: t["completed_date"])
    return result


def get_current_week_dates():
    """获取当前周一至周五的日期范围"""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    friday = monday + timedelta(days=4)
    return monday.strftime("%Y-%m-%d"), friday.strftime("%Y-%m-%d")


def get_week_dates_for_date(date_obj):
    """获取指定日期所在周的周一至周五"""
    monday = date_obj - timedelta(days=date_obj.weekday())
    friday = monday + timedelta(days=4)
    return monday.strftime("%Y-%m-%d"), friday.strftime("%Y-%m-%d")


def is_task_imported_recently(data, task_name, dedup_days=30):
    """检查任务是否在最近N天内已从Excel导入过"""
    cutoff = (datetime.now() - timedelta(days=dedup_days)).strftime("%Y-%m-%d")
    for rec in data.get("imported_records", []):
        if rec["task_name"] == task_name and rec["import_date"] >= cutoff:
            return True
    return False


def mark_task_imported(data, task_name):
    """记录任务已从Excel导入"""
    if "imported_records" not in data:
        data["imported_records"] = []
    data["imported_records"].append({
        "task_name": task_name,
        "import_date": datetime.now().strftime("%Y-%m-%d"),
    })
    # 清理超过dedup_days+7天的旧记录
    cfg = load_config()
    dedup_days = cfg.get("import_dedup_days", 30)
    cutoff = (datetime.now() - timedelta(days=dedup_days + 7)).strftime("%Y-%m-%d")
    data["imported_records"] = [
        r for r in data["imported_records"] if r["import_date"] >= cutoff
    ]


def backup_to_txt(data, filename=None):
    """将任务数据导出为TXT备份文件"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if filename is None:
        filename = f"清单备份_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(BACKUP_DIR, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(f"工作任务清单备份\n")
            f.write(f"备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")

            # 未完成任务
            pending = [t for t in data["tasks"] if not t["completed"]]
            f.write(f"【待完成任务】({len(pending)}个)\n")
            f.write("-" * 40 + "\n")
            for i, t in enumerate(pending, 1):
                f.write(f"{i}. {t['name']}")
                if t.get("deadline_info"):
                    f.write(f" [{t['deadline_info']}]")
                f.write(f"\n  创建日期: {t.get('created_date', '')}\n\n")

            # 已完成任务
            completed = [t for t in data["tasks"] if t["completed"]]
            completed.sort(key=lambda x: x.get("completed_date", ""))
            f.write(f"\n【已完成任务】({len(completed)}个)\n")
            f.write("-" * 40 + "\n")
            for i, t in enumerate(completed, 1):
                f.write(f"{i}. {t['name']}")
                if t.get("deadline_info"):
                    f.write(f" [{t['deadline_info']}]")
                f.write(f"\n  完成日期: {t.get('completed_date', '')}\n")
                f.write(f"  创建日期: {t.get('created_date', '')}\n\n")
        return True
    except Exception:
        return False


# ── 笔记功能 ──
import os as _os
NOTES_FILE = _os.path.join(_os.path.dirname(DATA_FILE), 'notes.txt')


def load_notes():
    """加载笔记内容"""
    if _os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""
    return ""


def save_notes(text):
    """保存笔记内容"""
    try:
        with open(NOTES_FILE, 'w', encoding='utf-8') as f:
            f.write(text)
        return True
    except Exception:
        return False
