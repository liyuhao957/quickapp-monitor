import os
import time
import signal
import multiprocessing
from datetime import datetime

from config import MONITOR_CONFIG, PROCESS_CONFIG, STATUS_MONITOR_CONFIG
from status_monitor import StatusMonitor
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
        self.running = True
        
        # 初始化状态监控
        self.status_monitor = StatusMonitor(STATUS_MONITOR_CONFIG['webhook_url'])
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

    def handle_signal(self, signum, frame):
        """处理进程信号"""
        print(f"收到信号 {signum}，准备停止所有监控...")
        self.running = False
        self.stop_all()

    def start_process(self, name, target_func, config):
        """启动单个监控进程"""
        if name in self.processes and self.processes[name].is_alive():
            print(f"{name} 已经在运行")
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
        print(f"{name} 启动成功 (PID: {process.pid})")

    def start_all(self):
        """启动所有监控进程"""
        print("开始启动所有监控进程...")
        
        # 发送启动通知
        if STATUS_MONITOR_CONFIG['startup_notify']:
            self.status_monitor.send_startup_notification()
        
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
                print(f"正在停止 {name}...")
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    print(f"{name} 未响应，强制终止")
                    process.kill()
            del self.processes[name]
            print(f"{name} 已停止")

    def stop_all(self):
        """停止所有监控进程"""
        print("正在停止所有监控进程...")
        for name in list(self.processes.keys()):
            self.stop_process(name)
        
        # 发送停止通知
        if STATUS_MONITOR_CONFIG['shutdown_notify']:
            self.status_monitor.send_shutdown_notification()
        
        print("所有监控进程已停止")

    def check_process_health(self):
        """检查进程健康状态"""
        try:
            for name, process in list(self.processes.items()):
                if not process.is_alive():
                    error_msg = f"{name} 已停止运行"
                    print(error_msg)
                    
                    # 发送错误通知
                    if STATUS_MONITOR_CONFIG['error_notify']:
                        self.status_monitor.send_error_notification(error_msg)
                    
                    if PROCESS_CONFIG['restart_on_crash']:
                        if self.restart_counts[name] < PROCESS_CONFIG['max_restarts']:
                            print(f"正在重启 {name}...")
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
                            error_msg = f"{name} 重启次数超过限制，不再重试"
                            print(error_msg)
                            if STATUS_MONITOR_CONFIG['error_notify']:
                                self.status_monitor.send_error_notification(error_msg)
            
            # 检查是否需要发送心跳
            if STATUS_MONITOR_CONFIG['heartbeat_notify'] and self.status_monitor.should_send_heartbeat():
                self.status_monitor.send_heartbeat()
                
        except Exception as e:
            error_msg = f"健康检查出错: {str(e)}"
            print(error_msg)
            if STATUS_MONITOR_CONFIG['error_notify']:
                self.status_monitor.send_error_notification(error_msg)

    def run(self):
        """运行监控管理器"""
        self.start_all()
        
        while self.running:
            self.check_process_health()
            time.sleep(PROCESS_CONFIG['health_check_interval'])

if __name__ == "__main__":
    manager = MonitorManager()
    manager.run() 