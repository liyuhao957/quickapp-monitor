import requests
import time
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup

class VersionMonitor:
    def __init__(self, url, webhook_url, check_interval=300):
        self.url = url
        self.webhook_url = webhook_url
        self.check_interval = check_interval
        self.last_hash = None
        self.last_content = None
        
    def get_page_content(self):
        """获取网页特定内容"""
        try:
            print("正在获取网页内容...")
            api_url = "https://svc-drcn.developer.huawei.com/community/servlet/consumer/cn/documentPortal/getDocumentById"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Content-Type': 'application/json',
                'Origin': 'https://developer.huawei.com',
                'Referer': 'https://developer.huawei.com/'
            }
            
            data = {
                "objectId": "quickapp-version-updates-0000001079803874",
                "version": "",
                "catalogName": "quickApp-Guides",
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
                    
                    # 查找所有版本更新信息的标题
                    version_titles = soup.find_all(['h1', 'h2', 'h3', 'h4'])
                    latest_version = None
                    latest_date = None
                    
                    # 遍历所有标题，找出最新的版本信息
                    for title in version_titles:
                        title_text = title.text.strip()
                        if '版本更新说明' in title_text and '（' in title_text:
                            version_number = title_text.split('版本更新说明')[0].strip()
                            version_date = title_text[title_text.find('（')+1:title_text.find('）')]
                            
                            # 找到第一个版本信息就退出，因为最新的版本会在最上面
                            latest_version = version_number
                            latest_date = version_date
                            
                            # 获取所有更新内容
                            updates = []
                            
                            # 1. 查找并解析组件部分
                            component_title = title.find_next(lambda tag: tag.name in ['h4'] and '组件' in tag.text)
                            if component_title:
                                component_table = component_title.find_next('table')
                                if component_table:
                                    updates.append("【组件更新】")
                                    # 解析组件表格
                                    rows = component_table.find_all('tr')[1:]
                                    for row in rows:
                                        cols = row.find_all('td')
                                        if len(cols) >= 2:
                                            component = cols[0].text.strip()
                                            description_cell = cols[1]  # 获取整个单元格
                                            
                                            # 分割描述文本，但保留HTML结构
                                            descriptions = []
                                            for text in description_cell.stripped_strings:
                                                if text.strip():
                                                    descriptions.append(text.strip())
                                            
                                            update_info = [f"【{component}】"]
                                            
                                            # 先添加更新内容
                                            main_content = descriptions[0] if descriptions else ""  # 第一段是主要内容
                                            for desc in main_content.split('。'):
                                                if desc.strip() and '详情请参见' not in desc:
                                                    update_info.append(f"• {desc.strip()}")
                                            
                                            # 再添加参考文档链接
                                            doc_link = description_cell.find('a')
                                            if doc_link:
                                                link_text = doc_link.text.strip()
                                                link_url = "https://developer.huawei.com/consumer/cn/doc/" + doc_link.get('href', '').replace('https://developer.huawei.com/consumer/cn/doc/', '')
                                                update_info.append(f"\n参考文档：{link_text} {link_url}")
                                            
                                            updates.append("\n".join(update_info))
                            
                            # 2. 查找并解析接口部分
                            interface_title = title.find_next(lambda tag: tag.name in ['h4'] and '接口' in tag.text)
                            if interface_title:
                                interface_table = interface_title.find_next('table')
                                if interface_table:
                                    updates.append("\n【接口更新】")
                                    # 解析接口表格
                                    rows = interface_table.find_all('tr')[1:]
                                    for row in rows:
                                        cols = row.find_all('td')
                                        if len(cols) >= 2:
                                            interface = cols[0].text.strip()
                                            description_cell = cols[1]  # 获取整个单元格
                                            
                                            # 分割描述文本，但保留HTML结构
                                            descriptions = []
                                            for text in description_cell.stripped_strings:
                                                if text.strip():
                                                    descriptions.append(text.strip())
                                            
                                            update_info = [f"【{interface}】"]
                                            
                                            # 先添加更新内容
                                            main_content = descriptions[0] if descriptions else ""  # 第一段是主要内容
                                            for desc in main_content.split('。'):
                                                if desc.strip() and '详情请参见' not in desc:
                                                    update_info.append(f"• {desc.strip()}")
                                            
                                            # 再添加参考文档链接
                                            doc_link = description_cell.find('a')
                                            if doc_link:
                                                link_text = doc_link.text.strip()
                                                link_url = "https://developer.huawei.com/consumer/cn/doc/" + doc_link.get('href', '').replace('https://developer.huawei.com/consumer/cn/doc/', '')
                                                update_info.append(f"\n参考文档：{link_text} {link_url}")
                                            
                                            updates.append("\n".join(update_info))
                            
                            result = {
                                'version': latest_version,
                                'updates': updates,
                                'date': latest_date
                            }
                            print(f"解析结果: {result}")
                            return result
                            break
                    else:
                        print("未找到版本标题")
                else:
                    print("API响应格式不正确")
            
            print("未找到目标内容")
            return None
            
        except Exception as e:
            print(f"发生错误: {str(e)}")
            print(f"错误类型: {type(e)}")
            return None
    
    def calculate_hash(self, content):
        """计算内容的哈希值"""
        return hashlib.md5(str(content).encode('utf-8')).hexdigest()
    
    def send_notification(self, message, msg_type="text"):
        """发送飞书通知"""
        headers = {
            'Content-Type': 'application/json'
        }
        
        if msg_type == "post":
            data = {
                "msg_type": "interactive",
                "card": {
                    "config": {
                        "wide_screen_mode": True
                    },
                    "header": {
                        "template": "blue",
                        "title": {
                            "content": "快应用版本说明更新通知",
                            "tag": "plain_text"
                        }
                    },
                    "elements": [
                        {
                            "tag": "markdown",
                            "content": message
                        },
                        {
                            "tag": "hr"
                        },
                        {
                            "tag": "note",
                            "elements": [
                                {
                                    "tag": "plain_text",
                                    "content": f"监控时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                }
                            ]
                        }
                    ]
                }
            }
        else:
            data = {
                "msg_type": "text",
                "content": {
                    "text": message
                }
            }
        
        try:
            response = requests.post(self.webhook_url, json=data, headers=headers)
            response.raise_for_status()
            print("通知发送成功")
        except requests.RequestException as e:
            print(f"发送通知失败: {e}")
    
    def monitor(self):
        """开始监控"""
        print(f"开始监控网页: {self.url}")
        
        try:
            # 获取当前信息并发送启动通知
            retries = 3  # 添加重试机制
            for attempt in range(retries):
                try:
                    current_content = self.get_page_content()
                    if current_content:
                        break
                except Exception as e:
                    if attempt == retries - 1:
                        raise
                    print(f"获取内容失败，{attempt + 1}/{retries} 次重试...")
                    time.sleep(5)
            
            if current_content:
                startup_message = self._format_notification(current_content, is_startup=True)
                self.send_notification(startup_message, msg_type="post")
                self.last_hash = self.calculate_hash(current_content)
                self.last_content = current_content
            
            while True:
                try:
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    content = self.get_page_content()
                    
                    if content:
                        # 比较版本号
                        if self._is_version_newer(content['version'], self.last_content['version']):
                            message = self._format_notification(content)
                            print(f"[{current_time}] 检测到新版本: {content['version']}")
                            self.send_notification(message, msg_type="post")
                            self.last_hash = self.calculate_hash(content)
                            self.last_content = content
                        else:
                            print(f"[{current_time}] 未检测到新版本")
                    
                    time.sleep(self.check_interval)
                    
                except KeyboardInterrupt:
                    print("\n收到退出信号，正在停止监控...")
                    shutdown_message = "🔔 版本说明更新监控服务已停止"
                    self.send_notification(shutdown_message, msg_type="post")
                    break
                    
                except Exception as e:
                    error_msg = f"监控出错: {str(e)}"
                    print(error_msg)
                    self.send_notification(error_msg)
                    time.sleep(60)  # 出错后等待1分钟再重试
            
        except KeyboardInterrupt:
            print("\n收到退出信号，正在停止监控...")
            shutdown_message = "🔔 版本更新监控服务已停止"
            self.send_notification(shutdown_message, msg_type="post")

    def _is_version_newer(self, new_version, old_version):
        """比较版本号"""
        try:
            # 移除版本号中的 'V' 前缀
            new_version = new_version.replace('V', '').strip()
            old_version = old_version.replace('V', '').strip()
            
            # 将版本号分割为数字列表
            new_parts = [int(x) for x in new_version.split('.')]
            old_parts = [int(x) for x in old_version.split('.')]
            
            return new_parts > old_parts
        except Exception as e:
            print(f"版本号比较出错: {str(e)}")
            return False

    def _format_notification(self, content, is_startup=False):
        """格式化通知消息"""
        if is_startup:
            return (
                "🔔 版本更新监控服务已启动\n"
                "|  类型  |  内容  |\n"
                "|:------:|:------|\n"
                f"|  版本  | `{content['version']}` |\n"
                f"|  日期  | `{content['date']}` |\n"
                "📋 更新内容\n" + 
                "\n\n".join([
                    content.replace('【组件更新】', '🔧 组件更新')
                           .replace('【接口更新】', '\n🔌 接口更新')
                           .replace('【', '📌 ')
                           .replace('】\n', '】')
                           .replace('\n\n参考文档：', '\n> 📚 ')
                           .replace('• ', '◦ ')
                    for content in content['updates']
                ]) +
                f"\n---\n⏱️ 监控间隔：`{self.check_interval}秒`"
            )
        else:
            return (
                "🚨 检测到版本更新！\n"
                "|  类型  |  内容  |\n"
                "|:------:|:------|\n"
                f"|  版本  | `{content['version']}` |\n"
                f"|  日期  | `{content['date']}` |\n"
                "📋 更新内容\n" + 
                "\n\n".join([
                    content.replace('【组件更新】', '🔧 组件更新')
                           .replace('【接口更新】', '\n🔌 接口更新')
                           .replace('【', '📌 ')
                           .replace('】', '')
                           .replace('\n\n参考文档：', '\n> 📚 ')
                           .replace('• ', '◦ ')
                    for content in content['updates']
                ]) +
                f"\n---\n🔗 [查看详情]({self.url})"
            )

# 使用示例
if __name__ == "__main__":
    target_url = "https://developer.huawei.com/consumer/cn/doc/quickApp-Guides/quickapp-version-updates-0000001079803874"
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/1a11a0f0-b246-423c-909f-5ebbbbf4e2f4"
    
    # 创建监控器（每5分钟检查一次）
    monitor = VersionMonitor(target_url, webhook_url, 300)
    
    # 开始监控
    monitor.monitor() 
    