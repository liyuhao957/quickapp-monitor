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
- 进程管理
  - 多进程并行监控
  - 自动健康检查
  - 进程崩溃自动重启
  - 每日心跳检测

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
# 监控配置
MONITOR_CONFIG = {
    # 荣耀快应用监控配置
    'honor': {
        'name': '荣耀快应用监控',
        'debugger_webhook': "your_webhook_url",
        'engine_webhook': "your_webhook_url",
        'check_interval': 300  # 5分钟
    },
    
    # 华为快应用加载器监控配置
    'huawei_loader': {
        'name': '华为快应用加载器监控',
        'url': "your_monitor_url",
        'webhook': "your_webhook_url",
        'check_interval': 300
    },
    
    # 华为快应用版本说明监控配置
    'huawei_version': {
        'name': '华为快应用版本监控',
        'url': "your_monitor_url",
        'webhook': "your_webhook_url",
        'check_interval': 300
    }
}

# 进程管理配置
PROCESS_CONFIG = {
    'health_check_interval': 60,  # 1分钟检查一次进程健康
    'restart_on_crash': True,     # 进程崩溃时自动重启
    'max_restarts': 3,            # 最大重启次数
    'restart_delay': 5            # 重启前等待时间（秒）
}

# 状态监控配置
STATUS_MONITOR_CONFIG = {
    'webhook_url': 'your_webhook_url',  # 状态监控机器人
    'startup_notify': True,   # 是否发送启动通知
    'shutdown_notify': True,  # 是否发送停止通知
    'error_notify': True,     # 是否发送错误通知
    'heartbeat_notify': True  # 是否发送心跳通知
}
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
├── status_monitor.py  # 状态监控服务
├── requirements.txt   # 项目依赖
├── docs/             # 文档目录
│   └── TASK_TEMPLATE.md  # 任务模板
└── .tasks/           # 任务记录
```

## 开发指南

### 代码规范
- 使用 Python 3.7+ 
- 遵循 PEP 8 编码规范
- 所有函数和类必须有文档字符串
- 关键代码需要添加注释

### 异常处理
- 使用 try-except 处理所有可能的异常
- 实现重试机制处理临时性错误
- 记录详细的错误信息
- 发送错误通知到飞书群

### 日志记录
- 使用 Python 标准库 logging
- 记录关键操作和错误信息
- 定期清理日志文件
- 支持不同级别的日志

### 测试
- 编写单元测试
- 进行集成测试
- 模拟各种异常情况
- 测试飞书通知功能

## 更新日志

### 2024-01-23
- 统一了消息通知格式
- 优化了下载链接的显示方式
- 改进了版本更新检测逻辑
- 增强了错误处理机制
- 添加了进程管理功能
- 实现了心跳检测机制
- 完善了配置管理系统

## 许可证

MIT License