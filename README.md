# Quick App Monitor

快应用监控工具，用于监控荣耀和华为快应用相关更新。

## 功能特点

- 监控荣耀快应用调试器和引擎更新
- 监控华为快应用加载器更新
- 监控华为快应用版本说明更新
- 支持飞书机器人通知
- 多进程管理
- 统一配置管理
- 自动重启机制
- 完整的日志记录

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

1. 在 `config.py` 中配置：
   - webhook URLs
   - 检查间隔
   - 日志设置
   - 进程管理参数

## 使用方法

运行统一监控程序：
```bash
python monitor_all.py
```

## 项目结构

- `monitor_all.py`: 统一启动脚本
- `config.py`: 配置文件
- `honorMonitor.py`: 荣耀快应用监控
- `huaweiJZQ.py`: 华为快应用加载器监控
- `huaweiSM.py`: 华为快应用版本监控
- `requirements.txt`: 项目依赖
- `docs/`: 文档目录
- `.tasks/`: 任务记录
- `logs/`: 日志目录

## 开发记录

详细的开发记录和任务进度可以在 `.tasks` 目录中查看。

## 许可证

MIT License 