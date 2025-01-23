import os
import time
import signal
import logging
import multiprocessing
from logging.handlers import RotatingFileHandler
from datetime import datetime

from config import MONITOR_CONFIG, LOG_CONFIG, PROCESS_CONFIG
from honorMonitor import HonorMonitor
from huaweiJZQ import WebMonitor
from huaweiSM import VersionMonitor

def run_honor_monitor(config):
    """运行荣耀快应用监控"""
    monitor = HonorMonitor(
        config['debugger_webhook'],
        config['engine_webhook'],
        config['check_interval']
    )
    monitor.monitor()

def run_huawei_loader_monitor(config):
    """运行华为加载器监控"""
    monitor = WebMonitor(
        config['url'],
        config['webhook'],
        config['check_interval']
    )
    monitor.monitor()

def run_huawei_version_monitor(config):
    """运行华为版本监控"""
    monitor = VersionMonitor(
        config['url'],
        config['webhook'],
        config['check_interval']
    )
    monitor.monitor()

class MonitorManager:
    def __init__(self):
        self.processes = {}
        self.restart_counts = {}
        self.setup_logging()
        self.running = True
        self.logger = logging.getLogger('MonitorManager')
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

    def setup_logging(self):
        """设置日志系统"""
        # 创建日志目录
        os.makedirs(LOG_CONFIG['log_dir'], exist_ok=True)
        
        # 设置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(LOG_CONFIG['level'])
        
        # 创建格式化器
        formatter = logging.Formatter(LOG_CONFIG['format'])
        
        # 创建文件处理器
        log_file = os.path.join(LOG_CONFIG['log_dir'], 'monitor_all.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=LOG_CONFIG['max_bytes'],
            backupCount=LOG_CONFIG['backup_count']
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    def handle_signal(self, signum, frame):
        """处理进程信号"""
        self.logger.info(f"收到信号 {signum}，准备停止所有监控...")
        self.running = False
        self.stop_all()

    def start_process(self, name, target_func, config):
        """启动单个监控进程"""
        if name in self.processes and self.processes[name].is_alive():
            self.logger.warning(f"{name} 已经在运行")
            return

        process = multiprocessing.Process(
            target=target_func,
            args=(config,),
            name=name,
            daemon=True
        )
        process.start()
        self.processes[name] = process
        self.restart_counts[name] = 0
        self.logger.info(f"{name} 启动成功 (PID: {process.pid})")

    def start_all(self):
        """启动所有监控进程"""
        self.logger.info("开始启动所有监控进程...")
        
        # 启动荣耀快应用监控
        self.start_process(
            'honor',
            run_honor_monitor,
            MONITOR_CONFIG['honor']
        )
        
        # 启动华为加载器监控
        self.start_process(
            'huawei_loader',
            run_huawei_loader_monitor,
            MONITOR_CONFIG['huawei_loader']
        )
        
        # 启动华为版本监控
        self.start_process(
            'huawei_version',
            run_huawei_version_monitor,
            MONITOR_CONFIG['huawei_version']
        )

    def stop_process(self, name):
        """停止单个监控进程"""
        if name in self.processes:
            process = self.processes[name]
            if process.is_alive():
                self.logger.info(f"正在停止 {name}...")
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    self.logger.warning(f"{name} 未响应，强制终止")
                    process.kill()
            del self.processes[name]
            self.logger.info(f"{name} 已停止")

    def stop_all(self):
        """停止所有监控进程"""
        self.logger.info("正在停止所有监控进程...")
        for name in list(self.processes.keys()):
            self.stop_process(name)
        self.logger.info("所有监控进程已停止")

    def check_process_health(self):
        """检查进程健康状态"""
        for name, process in list(self.processes.items()):
            if not process.is_alive():
                self.logger.warning(f"{name} 已停止运行")
                if PROCESS_CONFIG['restart_on_crash']:
                    if self.restart_counts[name] < PROCESS_CONFIG['max_restarts']:
                        self.logger.info(f"正在重启 {name}...")
                        time.sleep(PROCESS_CONFIG['restart_delay'])
                        self.restart_counts[name] += 1
                        
                        # 根据进程名获取对应的运行函数和配置
                        if name == 'honor':
                            target_func = run_honor_monitor
                            config = MONITOR_CONFIG['honor']
                        elif name == 'huawei_loader':
                            target_func = run_huawei_loader_monitor
                            config = MONITOR_CONFIG['huawei_loader']
                        elif name == 'huawei_version':
                            target_func = run_huawei_version_monitor
                            config = MONITOR_CONFIG['huawei_version']
                        
                        self.start_process(name, target_func, config)
                    else:
                        self.logger.error(f"{name} 重启次数超过限制，不再重试")

    def run(self):
        """运行监控管理器"""
        self.logger.info("=== 监控管理器启动 ===")
        self.start_all()
        
        try:
            while self.running:
                self.check_process_health()
                time.sleep(PROCESS_CONFIG['health_check_interval'])
        except KeyboardInterrupt:
            self.logger.info("收到中断信号")
        finally:
            self.stop_all()
            self.logger.info("=== 监控管理器已停止 ===")

if __name__ == "__main__":
    manager = MonitorManager()
    manager.run() 