import time
import requests
from datetime import datetime, timedelta

class StatusMonitor:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.start_time = time.time()
        self.last_heartbeat = None
    
    def send_notification(self, message):
        """发送通知到飞书"""
        try:
            response = requests.post(self.webhook_url, json=message)
            response.raise_for_status()
            print("状态通知发送成功")
        except Exception as e:
            print(f"状态通知发送失败: {str(e)}")
    
    def send_startup_notification(self):
        """发送服务启动通知"""
        message = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "template": "green",
                    "title": {
                        "content": "服务状态通知",
                        "tag": "plain_text"
                    }
                },
                "elements": [{
                    "tag": "div",
                    "text": {
                        "content": f"🟢 监控服务已启动\n启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        "tag": "lark_md"
                    }
                }]
            }
        }
        self.send_notification(message)
    
    def send_shutdown_notification(self):
        """发送服务停止通知"""
        message = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "template": "red",
                    "title": {
                        "content": "服务状态通知",
                        "tag": "plain_text"
                    }
                },
                "elements": [{
                    "tag": "div",
                    "text": {
                        "content": f"🔴 监控服务已停止\n停止时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        "tag": "lark_md"
                    }
                }]
            }
        }
        self.send_notification(message)
    
    def send_error_notification(self, error):
        """发送错误通知"""
        message = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "template": "red",
                    "title": {
                        "content": "服务异常通知",
                        "tag": "plain_text"
                    }
                },
                "elements": [{
                    "tag": "div",
                    "text": {
                        "content": (
                            f"⚠️ 监控服务发生异常\n"
                            f"错误信息：{error}\n"
                            f"发生时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        ),
                        "tag": "lark_md"
                    }
                }]
            }
        }
        self.send_notification(message)
    
    def send_heartbeat(self):
        """发送心跳消息"""
        uptime = time.time() - self.start_time
        days = int(uptime // 86400)
        hours = int((uptime % 86400) // 3600)
        minutes = int((uptime % 3600) // 60)
        
        message = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "template": "blue",
                    "title": {
                        "content": "服务心跳检测",
                        "tag": "plain_text"
                    }
                },
                "elements": [{
                    "tag": "div",
                    "text": {
                        "content": (
                            "💗 监控服务运行正常\n"
                            f"已运行时间：{days}天{hours}小时{minutes}分钟\n"
                            f"检测时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        ),
                        "tag": "lark_md"
                    }
                }]
            }
        }
        self.send_notification(message)
        self.last_heartbeat = time.time()
    
    def should_send_heartbeat(self):
        """检查是否应该发送心跳"""
        now = datetime.now()
        if self.last_heartbeat is None:
            return True
        
        last_heartbeat_time = datetime.fromtimestamp(self.last_heartbeat)
        next_heartbeat_time = last_heartbeat_time.replace(hour=0, minute=0, second=0) + timedelta(days=1)
        
        return now >= next_heartbeat_time