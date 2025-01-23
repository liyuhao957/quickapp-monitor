import requests
import time
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
import re

class WebMonitor:
    def __init__(self, url, webhook_url, interval=300):
        self.url = url
        self.webhook_url = webhook_url
        self.interval = interval
        self.last_hash = None
        self.last_content = None

    def monitor(self):
        """监控网页变化"""
        print(f"开始监控网页: {self.url}")
        
        try:
            # 先获取一次内容并发送启动通知
            print("正在获取初始内容...")
            content = self.get_page_content()
            result = self.parse_content(content)
            self.last_content = result
            self.last_hash = self.calculate_hash(result)
            
            startup_message = "开始监控华为快应用加载器更新..."
            self.send_notification(startup_message, msg_type="post")
            
            print(f"等待 {self.interval} 秒后再次检查...")
            time.sleep(self.interval)  # 先等待一个间隔
            
            while True:
                try:
                    print("\n开始新一轮检查...")  # 添加日志
                    content = self.get_page_content()
                    result = self.parse_content(content)
                    current_hash = self.calculate_hash(result)
                    
                    if current_hash != self.last_hash:
                        change_message = self.format_change_message(result)
                        self.send_notification(change_message, msg_type="post")
                        
                        self.last_hash = current_hash
                        self.last_content = result
                    
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 添加时间戳
                    print(f"[{current_time}] 等待 {self.interval} 秒后再次检查...")
                    time.sleep(self.interval)
                    
                except KeyboardInterrupt:
                    raise  # 向外层抛出中断信号
                except Exception as e:  # 添加错误处理
                    print(f"检查过程中出错: {str(e)}")
                    print("60秒后重试...")
                    time.sleep(60)
                
        except KeyboardInterrupt:
            print("\n收到退出信号，正在停止监控...")
            shutdown_message = {
                "msg_type": "interactive",
                "card": {
                    "config": {
                        "wide_screen_mode": True
                    },
                    "header": {
                        "template": "blue",
                        "title": {
                            "content": "快应用加载器更新通知",
                            "tag": "plain_text"
                        }
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": "🔔 加载器更新监控服务已停止"
                            }
                        }
                    ]
                }
            }
            self.send_notification(shutdown_message, msg_type="post")
    
    def get_page_content(self):
        """获取网页特定内容"""
        try:
            print("正在获取网页内容...")
            api_url = "https://svc-drcn.developer.huawei.com/community/servlet/consumer/cn/documentPortal/getDocumentById"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Content-Type': 'application/json',
                'Origin': 'https://developer.huawei.com',
                'Referer': 'https://developer.huawei.com/',
                'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site'
            }
            
            data = {
                "objectId": "quickapp-ide-download-0000001101172926",
                "version": "",
                "catalogName": "Tools-Library",
                "language": "cn"
            }
            
            print("发送POST请求...")
            response = requests.post(api_url, json=data, headers=headers)
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data['code'] == 0 and 'value' in data and 'content' in data['value']:
                    html_content = data['value']['content']['content']
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # 查找手机加载器部分
                    phone_loader_section = soup.find('div', id='section9347192715112')
                    if phone_loader_section:
                        # 查找所有加载器链接
                        all_links = phone_loader_section.find_all('a')
                        
                        # 筛选手机加载器的链接
                        phone_links = []
                        for link in all_links:
                            text = link.get_text().strip()
                            if text.startswith('HwQuickApp_Loader_Phone'):
                                phone_links.append(link)
                        
                        # 收集所有版本信息
                        versions = []
                        for link in phone_links:
                            text = link.get_text().strip()
                            href = link.get('href')
                            version = None
                            spec = None
                            
                            parent = link.find_parent('td') or link.parent
                            if parent:
                                row = parent.find_parent('tr')
                                row_text = row.get_text() if row else parent.get_text()
                                
                                version_match = re.search(r'V?(\d+\.\d+\.\d+\.\d+)', text)
                                spec_match = re.search(r'支持(\d{4})规范|（支持(\d{4})规范）', row_text)
                                
                                if version_match:
                                    version = version_match.group(1)
                                if spec_match:
                                    spec = spec_match.group(1) or spec_match.group(2)
                                
                                if version and spec:
                                    versions.append({
                                        'text': text,
                                        'url': href,
                                        'version': version,
                                        'spec': spec
                                    })
                        
                        if versions:
                            versions.sort(key=lambda x: [int(i) for i in x['version'].split('.')], reverse=True)
                            return versions[0]
                        
                        raise ValueError("未找到有效的版本信息")
                    
                    raise ValueError("未找到手机加载器部分")
                
                raise ValueError(f"API请求失败: {response.status_code}")
                
            raise ValueError(f"API请求失败: {response.status_code}")
            
        except Exception as e:
            print(f"获取内容失败: {str(e)}")
            raise
    
    def calculate_hash(self, content):
        """计算内容的哈希值"""
        return hashlib.md5(str(content).encode('utf-8')).hexdigest()
    
    def send_notification(self, message, msg_type="text"):
        """发送通知到飞书"""
        headers = {
            'Content-Type': 'application/json'
        }
        
        if isinstance(message, dict):
            content = message
        elif msg_type == "post":
            if "开始监控" in message:
                content = {
                    "msg_type": "interactive",
                    "card": {
                        "config": {
                            "wide_screen_mode": True
                        },
                        "header": {
                            "template": "blue",
                            "title": {
                                "content": "快应用加载器更新通知",
                                "tag": "plain_text"
                            }
                        },
                        "elements": [
                            {
                                "tag": "div",
                                "text": {
                                    "tag": "lark_md",
                                    "content": (
                                        "🔔 加载器更新监控服务已启动\n\n"
                                        "|  类型  |  内容  |\n"
                                        "|:------:|:------|\n"
                                        f"|  版本  | `{self.last_content['version']}` |\n"
                                        f"|  规范  | `{self.last_content['spec']}` |\n"
                                        f"|  文件  | `{self.last_content['text']}` |\n\n"
                                        f"📥 下载链接：{self.last_content['url']}\n\n"
                                        f"⏱️ 监控间隔：`{self.interval}秒`"
                                    )
                                }
                            }
                        ]
                    }
                }
            else:
                current_content = self.get_page_content()  # 获取最新内容
                content = {
                    "msg_type": "interactive",
                    "card": {
                        "config": {
                            "wide_screen_mode": True
                        },
                        "header": {
                            "template": "blue",
                            "title": {
                                "content": "快应用加载器更新通知",
                                "tag": "plain_text"
                            }
                        },
                        "elements": [
                            {
                                "tag": "div",
                                "text": {
                                    "tag": "lark_md",
                                    "content": (
                                        "🚨 检测到加载器更新！\n\n"
                                        "|  类型  |  内容  |\n"
                                        "|:------:|:------|\n"
                                        f"|  版本  | `{current_content['version']}` |\n"
                                        f"|  规范  | `{current_content['spec']}` |\n"
                                        f"|  文件  | `{current_content['text']}` |\n\n"
                                        f"📥 下载链接：{current_content['url']}"
                                    )
                                }
                            }
                        ]
                    }
                }
        else:
            content = {
                "msg_type": "text",
                "content": {
                    "text": message
                }
            }

        try:
            response = requests.post(self.webhook_url, json=content, headers=headers)
            response.raise_for_status()
            print("通知发送成功")
        except requests.RequestException as e:
            print(f"发送通知失败: {e}")
    
    def parse_content(self, content):
        """解析网页内容"""
        required_fields = ['text', 'url', 'version', 'spec']
        
        if isinstance(content, dict):
            # 验证必要字段
            if all(field in content for field in required_fields):
                # 检查版本号和规范版本号的变化
                if self.last_content:
                    # 解析版本号字符串为数字列表，如 "14.4.1.300" -> [14, 4, 1, 300]
                    current_version = [int(x) for x in content['version'].split('.')]
                    last_version = [int(x) for x in self.last_content['version'].split('.')]
                    
                    # 比较版本号
                    if current_version > last_version:
                        print(f"检测到版本升级: {self.last_content['version']} -> {content['version']}")
                    
                    # 比较规范版本号
                    if int(content['spec']) > int(self.last_content['spec']):
                        print(f"检测到规范版本升级: {self.last_content['spec']} -> {content['spec']}")
                
                return content
            raise ValueError("缺少必要字段")
        
        # 如果是其他格式，需要解析
        result = {
            'text': content.get('text', ''),
            'url': content.get('url', ''),
            'version': content.get('version', ''),
            'spec': content.get('spec', '')
        }
        
        # 验证字段不为空
        if not all(result.values()):
            raise ValueError("解析结果包含空字段")
        
        # 检查规范版本号的变化
        if self.last_content and int(result['spec']) > int(self.last_content['spec']):
            print(f"检测到规范版本升级: {self.last_content['spec']} -> {result['spec']}")
        
        return result
    
    def format_change_message(self, content):
        """格式化变化通知消息"""
        return (
            f"检测到加载器更新！\n"
            f"文件名: {content['text']}\n"
            f"版本号: {content['version']}\n"
            f"规范版本: {content['spec']}\n"
            f"下载链接: {content['url']}"
        )

# 使用示例
if __name__ == "__main__":
    target_url = "https://developer.huawei.com/consumer/cn/doc/Tools-Library/quickapp-ide-download-0000001101172926"
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/b5d78e2d-502d-42c7-81d2-48eebf43224e"
    
    # 创建监控器
    monitor = WebMonitor(target_url, webhook_url)
    
    # 开始监控
    monitor.monitor() 