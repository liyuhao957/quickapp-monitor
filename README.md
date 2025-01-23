# Quick App Monitor

快应用监控工具，用于监控荣耀和华为快应用相关更新。

## 功能特点

### 荣耀快应用监控
- 监控调试器更新
  - 版本号、引擎版本、荣耀版本、联盟版本等信息
  - 功能更新列表
  - 下载链接
- 监控引擎版本更新
  - 版本号、上线时间
  - 荣耀引擎版本、联盟版本
  - 详细的功能更新说明
  - 下载链接

### 华为快应用监控
- 监控加载器更新
  - 版本号、规范版本
  - 文件信息
  - 下载链接
- 监控版本说明更新
  - 组件更新
  - 接口更新
  - 详细的功能说明

### 通用特性
- 飞书机器人通知
  - 美观的卡片消息
  - 表格化的版本信息
  - 格式化的更新内容
  - 可点击的下载链接
- 智能的版本比对
  - 版本号对比
  - 内容变化检测
  - 避免重复通知
- 稳定性保障
  - 异常自动重试
  - 完整的错误处理
  - 详细的日志记录

## 安装

1. 克隆仓库：
```bash
git clone git@github.com:liyuhao957/quickapp-monitor.git
cd quickapp-monitor
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置

在 `config.py` 中配置以下参数：

```python
# 飞书机器人 Webhook URLs
HONOR_DEBUGGER_WEBHOOK = "your_webhook_url"
HONOR_ENGINE_WEBHOOK = "your_webhook_url"
HUAWEI_LOADER_WEBHOOK = "your_webhook_url"
HUAWEI_VERSION_WEBHOOK = "your_webhook_url"

# 检查间隔（秒）
CHECK_INTERVAL = 300  # 默认5分钟

# 监控开关
ENABLE_HONOR_MONITOR = True
ENABLE_HUAWEI_MONITOR = True
```

## 使用方法

### 统一监控
运行所有监控：
```bash
python monitor_all.py
```

### 单独监控
运行特定监控：
```bash
# 荣耀快应用监控
python honorMonitor.py

# 华为加载器监控
python huaweiJZQ.py

# 华为版本监控
python huaweiSM.py
```

## 项目结构

```
quickapp-monitor/
├── monitor_all.py     # 统一启动脚本
├── config.py          # 配置文件
├── honorMonitor.py    # 荣耀快应用监控
├── huaweiJZQ.py      # 华为加载器监控
├── huaweiSM.py       # 华为版本监控
├── requirements.txt   # 项目依赖
├── docs/             # 文档目录
│   └── TASK_TEMPLATE.md  # 任务模板
└── .tasks/           # 任务记录
```

## 开发记录

详细的开发记录和任务进度可以在 `.tasks` 目录中查看，每个任务都按照 `docs/TASK_TEMPLATE.md` 的格式进行记录。

## 更新日志

### 2024-01-23
- 统一了消息通知格式
- 优化了下载链接的显示方式
- 改进了版本更新检测逻辑
- 增强了错误处理机制

## 许可证

MIT License