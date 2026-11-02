# 工作任务清单 (Work Task Planner)

<p align="center">
  <img src="assets/icon.png" alt="工作任务清单图标" width="120">
</p>

<p align="center">
  <strong>一款离线运行的 Windows 桌面待办工具：管任务、算下班倒计时、攒周报、翻日历。</strong>
</p>

<p align="center">
  <a href="https://github.com/jhtfly/work-task-planner/releases/latest">下载程序</a> ·
  <a href="#功能特性">功能特性</a> ·
  <a href="#excel-自动导入">Excel 导入</a> ·
  <a href="#从源码运行">源码运行</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows%207%20%7C%2010%20%7C%2011-blue" alt="Platform">
  <img src="https://img.shields.io/badge/Python-3.8%2B-yellow" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/Dependencies-仅%20openpyxl-lightgrey" alt="Dependencies">
</p>

---

## 项目简介

面向日常办公场景的单机待办清单工具。所有数据保存在程序目录本地，**不联网、不上传、无账号**。适合需要把「琐碎任务 + 截止时限 + 周报汇总」放在一个窗口里管理，又要求数据不出本机的工作环境。

界面自上而下为一条纵向滚动流：时钟头部 → 今日任务 → 今日已完成 → 本周周报 → 日历 → 笔记。窗口默认 900×800，可缩放。

## 功能特性

| 模块 | 能力 |
|---|---|
| 时钟头部 | 显示当日日期、实时时间（数字 + 模拟时钟表盘）、距下班倒计时；上午班与下午班分别计算，非上班时段不显示倒计时 |
| 今日工作任务 | 任务自动编号；点击任务名就地编辑，回车即新增下一条；时限选填；勾选完成后自动归入「今日已完成」。未完成任务跨天保留 |
| 今日已完成 | 汇总当天完成的任务，支持撤销完成状态 |
| 本周周报 | 按当前自然周（周一至周五）汇总已完成任务，署名可自定义；标题与清单支持一键复制，复制内容仅含标题、序号、任务名 |
| 日历 | 按年月翻页，点击任意日期可查看当日与当周已完成任务，同样支持一键复制 |
| 笔记区 | 自由编辑、即时保存、一键复制 |
| 设置 | 夏冬季作息时间、Excel 导入参数、周报署名、主题配色（内置调色板） |
| 数据备份 | 每次关闭自动将清单导出为 TXT 存入 `清单备份/` 目录，另设手动备份与全局重置按钮 |

### 作息时间

内置夏季、冬季两套作息，按当前月份自动切换（夏季默认 5–9 月，可在配置中调整），全部可在设置界面修改。程序内置的初始值如下：

| 季节 | 上午 | 下午 |
|---|---|---|
| 夏季 | 08:30 – 11:30 | 14:00 – 17:30 |
| 冬季 | 08:30 – 11:30 | 14:30 – 17:00 |

> 注：与你所在单位的实际作息不一致时，直接在「设置 → 作息时间」中修改即可，保存后立即生效。

## 下载与安装

前往 [Releases](https://github.com/jhtfly/work-task-planner/releases/latest) 下载最新版：

1. 下载 `work-task-planner-v1.0.0.exe`（单文件，无需安装、无需 Python 环境）；
2. 放入任意**可写的文件夹**（建议避开 `C:\Program Files`，程序会在同级目录读写数据）；
3. 双击运行。首次启动会自动创建 `工作任务`、`清单备份` 两个子目录及数据文件。

> 兼容 **64 位** Windows 7 SP1 及以上（不支持 32 位系统）。程序以 Python 3.8.10 64 位构建，规避 Win7 下 `api-ms-win-core-path-l1-1-0.dll` 缺失的兼容性问题。

## Excel 自动导入

程序启动时会扫描 `工作任务` 文件夹下的**第一个 Excel 文件**，按规则挑选紧急任务加入今日清单，也可在界面上手动点击刷新。

导入规则：

- 读取指定工作表的 **D 列**作为任务名称、**O 列**作为距截止天数；
- 仅导入「剩余天数 ≥ 0 且 < 7 天」的任务（阈值可改）；
- 已过期（负数）或无天数的行会被跳过；
- 同一任务 30 天内不重复导入（去重天数可改）；
- 工作表名称、任务列、天数列、阈值、去重天数均在「设置 → Excel 设置」中配置。

仓库内的 `V1.0/工作任务/工作任务示例表.xlsx` 是一份**纯示例数据**，可直接用于试跑导入功能。把真实数据表放进同一目录前，请先确认 `.gitignore` 已生效——仓库默认忽略该目录下除示例表以外的所有 Excel 文件。

## 目录结构

```
work-task-planner/
├─ V1.0/                    # 当前版本目录
│  ├─ main.py               # 程序入口
│  ├─ app/
│  │  ├─ config.py          # 配置读写与默认值
│  │  ├─ data.py            # 任务数据与 TXT 备份
│  │  ├─ widgets.py         # 各面板组件
│  │  ├─ calendar_widget.py # 日历组件
│  │  ├─ settings.py        # 设置对话框
│  │  └─ excel_importer.py  # Excel 导入逻辑
│  ├─ 图标.ico / 图标.png
│  └─ 工作任务/
│     └─ 工作任务示例表.xlsx  # 脱敏示例数据
├─ assets/icon.png           # README 用图标
├─ docs/需求说明.md          # 功能需求书（脱敏版）
├─ requirements.txt
├─ LICENSE
└─ README.md
```

运行时会在 `V1.0/` 下生成：`data.json`（任务数据）、`config.json`（用户配置）、`notes.txt`（笔记）、`清单备份/`（TXT 备份）。这些均为个人数据，已在 `.gitignore` 中排除。

## 从源码运行

```bash
git clone https://github.com/jhtfly/work-task-planner.git
cd work-task-planner
pip install -r requirements.txt
python V1.0/main.py
```

要求 Python 3.8+，图形界面基于 tkinter（Python 官方安装包自带）。未安装 `openpyxl` 时程序仍可正常启动，仅 Excel 自动导入不可用，界面会给出提示。

## 从源码打包

```bash
pip install pyinstaller openpyxl
cd V1.0
pyinstaller -F -w -i 图标.ico --add-data "图标.ico;." --name "工作任务清单" main.py
```

产物位于 `V1.0/dist/工作任务清单.exe`。

打包注意事项：

- 若要兼容 Windows 7，必须使用 **Python 3.8.10 64 位** 环境（3.9+ 在 Win7 下会因 `api-ms-win-core-path-l1-1-0.dll` 缺失而无法启动）；
- 该 Python 环境必须自带 **tkinter**（官方安装包默认包含；部分精简版或嵌入式分发包不含，打包后会因 `missing module named tkinter` 而无法运行，可用 `python -c "import tkinter"` 先行验证）；
- 打包环境需安装 `openpyxl`，否则生成的 exe 缺失 Excel 导入能力。

## 数据与隐私

- 程序**完全离线**，不发起任何网络请求，不含统计上报与自动更新。
- 本仓库不含任何真实业务数据：任务清单、笔记、个人姓名、机构信息均已移除或替换为通用示例。
- 默认署名为「张三」，请在设置界面改为自己的姓名或岗位名称。

## 已知限制

- 周报周期按自然周周一至周五计算，**不处理法定节假日与调休**。
- Excel 导入只读取单个工作表，不支持一次导入多个文件。
- 界面基于 tkinter，主题为自定义配色方案，非系统原生控件外观。

## 许可证

[MIT](LICENSE)
