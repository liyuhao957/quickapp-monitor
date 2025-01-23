import requests
import time
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
import json
import re

class HonorMonitor:
    def __init__(self, debugger_webhook_url, engine_webhook_url, check_interval=300):
        self.api_url = "https://developer.honor.com/document/portal/tree/101380"
        self.debugger_webhook_url = debugger_webhook_url
        self.engine_webhook_url = engine_webhook_url
        self.check_interval = check_interval
        self.last_debugger_hash = None
        self.last_engine_hash = None
        self.last_debugger_content = None
        self.last_engine_content = None

    def get_page_content(self):
        """获取页面内容"""
        try:
            print("正在获取页面内容...")
            params = {
                "platformNo": "10001",
                "lang": "cn"
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://developer.honor.com/cn/doc/guides/101380',
                'terminal-lang': 'cn',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-platform': '"macOS"',
                'sec-ch-ua-mobile': '?0',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin'
            }
            
            print("发送请求...")
            print(f"URL: {self.api_url}")
            print(f"参数: {params}")
            print(f"请求头: {headers}")
            
            response = requests.get(self.api_url, params=params, headers=headers)
            response.raise_for_status()
            
            print("\n=== 响应状态码 ===")
            print(f"Status Code: {response.status_code}")
            print("===================")
            
            if response.status_code == 200:
                json_data = response.json()
                if json_data.get('code') == '200':
                    # 从 JSON 中提取 HTML 内容
                    html_content = json_data.get('data', {}).get('documentInfo', {}).get('text', '')
                    
                    print("\n=== HTML 内容（前1000字符）===")
                    print(html_content[:1000])
                    print("===================\n")
                    
                    return html_content
                else:
                    raise ValueError(f"API返回错误代码: {json_data.get('code')}")
            else:
                raise ValueError(f"HTTP状态码错误: {response.status_code}")
            
        except Exception as e:
            print(f"获取页面内容失败: {str(e)}")
            print(f"错误类型: {type(e)}")
            if hasattr(e, 'response'):
                print(f"响应状态码: {e.response.status_code}")
                print(f"响应内容: {e.response.text[:500]}")
            raise

    def parse_debugger_info(self, soup):
        """解析调试器信息"""
        try:
            # 添加调试输出
            print("\n=== HTML 结构 ===")
            print("找到的所有 h1 标签:")
            for h1 in soup.find_all('h1'):
                print(f"ID: {h1.get('id', 'No ID')}, 文本: {h1.text}")
            print("=================\n")
            
            # 修改 ID 的匹配方式，去掉引号
            debugger_section = soup.find('h1', id=lambda x: x and 'h1-1717124946965' in x)
            if not debugger_section:
                raise ValueError("未找到调试器下载部分")

            table = debugger_section.find_next('table')
            if not table:
                raise ValueError("未找到调试器下载表格")

            rows = table.find_all('tr')[1:]  # 跳过表头
            latest_debugger = None

            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 6:
                    debugger_info = {
                        "快应用引擎版本号": cols[0].get_text().strip(),
                        "荣耀引擎版本号": cols[1].get_text().strip(),
                        "快应用联盟平台版本号": cols[2].get_text().strip(),
                        "下载地址": cols[3].find('a')['href'] if cols[3].find('a') else "",
                        "调试器版本号": cols[4].get_text().strip(),
                        "功能": [item.strip() for item in cols[5].get_text().split('\n') if item.strip()]
                    }
                    
                    if not latest_debugger:
                        latest_debugger = debugger_info

            return latest_debugger
        except Exception as e:
            print(f"解析调试器信息失败: {str(e)}")
            raise

    def parse_feature_text(self, text):
        """解析功能文本"""
        features = []
        
        # 先按功能类型标记分割
        pattern = r'(新增：|优化：|废弃：)'
        parts = re.split(pattern, text)
        
        current_type = None
        current_text = ''
        
        for part in parts:
            if part in ['新增：', '优化：', '废弃：']:
                # 如果已有累积的文本，保存它
                if current_type and current_text:
                    clean_text = self.clean_feature_text(f"{current_type}{current_text}")
                    if clean_text:
                        features.append(clean_text)
                current_type = part
                current_text = ''
            elif part.strip():
                current_text = part.strip()
            
        # 处理最后一个功能项
        if current_type and current_text:
            clean_text = self.clean_feature_text(f"{current_type}{current_text}")
            if clean_text:
                features.append(clean_text)
        
        return features

    def parse_engine_info(self, soup):
        """解析引擎版本更新日志"""
        try:
            print("\n=== 开始解析引擎版本信息 ===")
            
            # 查找最新版本链接
            version_links = soup.find_all('a', string=re.compile(r'V\d+\.\d+\.\d+\.\d+'))
            if not version_links:
                raise ValueError("未找到版本信息")
            
            # 获取最新版本信息（第一个版本链接）
            version_link = version_links[0]
            version_number = version_link.get_text(strip=True)
            download_url = version_link.get('href', '')  # 获取下载链接
            print(f"\n找到最新版本: {version_number}")
            print(f"下载链接: {download_url}")
            
            # 获取上线时间
            release_date = ""
            parent_p = version_link.find_parent('p')
            if parent_p:
                next_p = parent_p.find_next_sibling('p')
                if next_p:
                    date_text = next_p.get_text(strip=True)
                    if date_text.startswith('20') or '上线时间' in date_text:
                        release_date = date_text.replace('上线时间', '').strip()
                        print(f"上线时间: {release_date}")
            
            # 获取引擎版本信息
            print("\n查找版本表格...")
            engine_versions = {}
            # 查找最新版本下的第一个表格
            current_element = version_link
            while current_element:
                if current_element.name == 'table':
                    print("找到版本表格")
                    rows = current_element.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) == 2:
                            key = cols[0].get_text(strip=True)
                            value = cols[1].get_text(strip=True)
                            engine_versions[key] = value
                            print(f"表格内容: {key} = {value}")
                    break
                current_element = current_element.find_next()
            
            # 获取功能更新列表
            print("\n=== 查找功能更新 ===")
            features = []  # 使用列表替代集合，保持原始顺序
            
            # 找到版本更新日志的容器
            version_container = None
            for h1 in soup.find_all('h1'):
                if '快应用引擎版本更新日志' in h1.get_text():
                    version_container = h1.find_parent()
                    print("找到版本更新日志容器")
                    break
            
            if not version_container:
                raise ValueError("未找到版本更新日志容器")
            
            # 在容器中查找当前版本的内容
            current_version_content = None
            next_version_content = None
            in_feature_list = False
            
            # 遍历所有内容
            for element in version_container.descendants:
                if not hasattr(element, 'get_text'):
                    continue
                
                text = element.get_text(strip=True)
                if not text:
                    continue
                
                print(f"检查元素: {text[:100]}...")
                
                # 找到当前版本
                if version_number in text and not current_version_content:
                    current_version_content = element
                    print(f"找到当前版本内容: {text}")
                    continue
                
                # 如果已找到当前版本，开始收集功能
                if current_version_content and not next_version_content:
                    # 检查是否是下一个版本
                    if any(v.get_text() in text for v in version_links[1:]):
                        next_version_content = element
                        print(f"找到下一个版本: {text}")
                        break
                    
                    # 检查是否进入功能列表区域
                    if text == "功能" or text.startswith("功能："):
                        in_feature_list = True
                        print("进入功能列表区域")
                        continue
                    
                    # 如果在功能列表区域内，收集功能
                    if in_feature_list:
                        # 检查是否是功能描述
                        if any(text.startswith(prefix) for prefix in ['●', '新增', '优化', '废弃']):
                            # 清理文本
                            clean_text = text.replace('●', '').strip()
                            
                            # 解析功能文本
                            parsed_features = self.parse_feature_text(clean_text)
                            
                            # 添加非重复的功能，保持原始顺序
                            for feature in parsed_features:
                                if not self.is_duplicate_feature(feature, features):
                                    features.append(feature)
                                    print(f"找到功能: {feature}")
            
            print(f"\n共找到 {len(features)} 个功能更新")
            
            result = {
                "版本号": version_number,
                "上线时间": release_date,
                "下载地址": download_url,  # 添加下载链接
                "引擎版本": engine_versions,
                "功能": features  # 直接使用列表，不进行排序
            }
            
            print("\n=== 解析结果 ===")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print("===================\n")
            
            return result
            
        except Exception as e:
            print(f"\n解析引擎版本信息失败: {str(e)}")
            print(f"错误类型: {type(e)}")
            print("===================\n")
            raise

    def clean_feature_text(self, text):
        """清理功能文本"""
        try:
            # 移除特殊字符但保留换行
            text = text.strip()
            
            # 规范化标点符号
            text = text.replace(':', '：')
            
            # 确保以功能类型开头
            if not any(text.startswith(prefix) for prefix in ['新增：', '优化：', '废弃：']):
                print(f"文本不以功能类型开头: {text}")
                return None
            
            # 移除重复的功能类型标记
            text = re.sub(r'([新增|优化|废弃])[：:]\s*\1', r'\1：', text)
            
            # 移除多余的空格，但保留换行
            text = re.sub(r'[ \t]+', ' ', text)
            
            print(f"清理后的文本: {text}")
            return text
            
        except Exception as e:
            print(f"清理文本失败: {str(e)}")
            return None

    def calculate_hash(self, content):
        """计算内容的哈希值"""
        return hashlib.md5(json.dumps(content, sort_keys=True).encode('utf-8')).hexdigest()

    def send_notification(self, title, content, is_debugger=True):
        """发送飞书通知"""
        try:
            webhook_url = self.debugger_webhook_url if is_debugger else self.engine_webhook_url
            message = {
                "msg_type": "interactive",
                "card": {
                    "config": {
                        "wide_screen_mode": True
                    },
                    "header": {
                        "template": "blue",
                        "title": {
                            "content": title,
                            "tag": "plain_text"
                        }
                    },
                    "elements": [
                        {
                            "tag": "markdown",
                            "content": content
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

            response = requests.post(
                webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            print(f"通知发送成功: {title}")
        except Exception as e:
            print(f"发送通知失败: {str(e)}")

    def format_debugger_message(self, debugger_info, is_startup=False):
        """格式化调试器通知消息"""
        prefix = "🔔 监控服务已启动" if is_startup else "🚨 检测到调试器更新"
        
        return (
            f"{prefix}\n\n"
            "|  类型  |  内容  |\n"
            "|:------:|:------|\n"
            f"|  版本号  | `{debugger_info['调试器版本号']}` |\n"
            f"|  引擎版本  | `{debugger_info['快应用引擎版本号']}` |\n"
            f"|  荣耀版本  | `{debugger_info['荣耀引擎版本号']}` |\n"
            f"|  联盟版本  | `{debugger_info['快应用联盟平台版本号']}` |\n\n"
            "📋 更新内容\n" +
            "\n".join([f"• {item}" for item in debugger_info['功能']]) +
            f"\n\n📥 [下载地址]({debugger_info['下载地址']})" +
            (f"\n\n⏱️ 监控间隔：`{self.check_interval}秒`" if is_startup else "")
        )

    def format_engine_message(self, engine_info, is_startup=False):
        """格式化引擎版本通知消息"""
        prefix = "🔔 监控服务已启动" if is_startup else "🚨 检测到引擎版本更新"
        
        return (
            f"{prefix}\n\n"
            "|  类型  |  内容  |\n"
            "|:------:|:------|\n"
            f"|  版本号  | `{engine_info['版本号']}` |\n"
            f"|  上线时间  | `{engine_info['上线时间']}` |\n"
            f"|  荣耀版本  | `{engine_info['引擎版本'].get('荣耀快应用引擎平台', '')}` |\n"
            f"|  联盟版本  | `{engine_info['引擎版本'].get('快应用联盟平台', '')}` |\n\n"
            "📋 更新内容\n" +
            "\n".join([f"• {item}" for item in engine_info['功能']]) +
            f"\n\n📥 [下载地址]({engine_info.get('下载地址', '暂无')})" +
            (f"\n\n⏱️ 监控间隔：`{self.check_interval}秒`" if is_startup else "")
        )

    def compare_versions(self, new_version, old_version):
        """比较两个版本号的大小
        返回: 
            1: new_version 更新
            0: 版本相同
            -1: old_version 更新
        """
        try:
            # 移除版本号中的 'V' 前缀
            new_ver = new_version.replace('V', '').strip()
            old_ver = old_version.replace('V', '').strip()
            
            # 将版本号分割为数字列表
            new_parts = [int(x) for x in new_ver.split('.')]
            old_parts = [int(x) for x in old_ver.split('.')]
            
            # 比较每个部分
            for new, old in zip(new_parts, old_parts):
                if new > old:
                    return 1
                elif new < old:
                    return -1
            
            # 如果前面都相同，比较长度
            if len(new_parts) > len(old_parts):
                return 1
            elif len(new_parts) < len(old_parts):
                return -1
            
            return 0
        except Exception as e:
            print(f"版本比较出错: {str(e)}")
            return 0

    def is_content_updated(self, new_content, old_content, content_type="debugger"):
        """检查内容是否有更新
        content_type: "debugger" 或 "engine"
        """
        try:
            if not old_content:
                return True
                
            if content_type == "debugger":
                # 比较调试器版本号
                version_compare = self.compare_versions(
                    new_content['调试器版本号'],
                    old_content['调试器版本号']
                )
                if version_compare > 0:
                    print(f"检测到调试器版本更新: {old_content['调试器版本号']} -> {new_content['调试器版本号']}")
                    return True
                    
                # 比较引擎版本号
                engine_compare = self.compare_versions(
                    new_content['快应用引擎版本号'],
                    old_content['快应用引擎版本号']
                )
                if engine_compare > 0:
                    print(f"检测到引擎版本更新: {old_content['快应用引擎版本号']} -> {new_content['快应用引擎版本号']}")
                    return True
                    
            elif content_type == "engine":
                # 比较引擎版本号
                version_compare = self.compare_versions(
                    new_content['版本号'],
                    old_content['版本号']
                )
                if version_compare > 0:
                    print(f"检测到引擎版本更新: {old_content['版本号']} -> {new_content['版本号']}")
                    return True
                    
                # 比较功能列表
                new_features = set(new_content['功能'])
                old_features = set(old_content['功能'])
                if new_features != old_features:
                    print("检测到功能更新")
                    print("新增功能:", new_features - old_features)
                    return True
            
            return False
            
        except Exception as e:
            print(f"内容比较出错: {str(e)}")
            return False

    def monitor(self):
        """开始监控"""
        print(f"开始监控荣耀快应用更新...")
        
        try:
            # 获取初始内容并发送启动通知
            html_content = self.get_page_content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            debugger_info = self.parse_debugger_info(soup)
            engine_info = self.parse_engine_info(soup)
            
            self.last_debugger_content = debugger_info
            self.last_engine_content = engine_info
            
            # 发送启动通知
            self.send_notification(
                "荣耀快应用调试器监控",
                self.format_debugger_message(debugger_info, is_startup=True),
                is_debugger=True
            )
            self.send_notification(
                "荣耀快应用引擎版本监控",
                self.format_engine_message(engine_info, is_startup=True),
                is_debugger=False
            )
            
            while True:
                try:
                    print("\n开始新一轮检查...")
                    html_content = self.get_page_content()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # 检查调试器更新
                    debugger_info = self.parse_debugger_info(soup)
                    if self.is_content_updated(debugger_info, self.last_debugger_content, "debugger"):
                        self.send_notification(
                            "荣耀快应用调试器更新",
                            self.format_debugger_message(debugger_info),
                            is_debugger=True
                        )
                        self.last_debugger_content = debugger_info
                    
                    # 检查引擎版本更新
                    engine_info = self.parse_engine_info(soup)
                    if self.is_content_updated(engine_info, self.last_engine_content, "engine"):
                        self.send_notification(
                            "荣耀快应用引擎版本更新",
                            self.format_engine_message(engine_info),
                            is_debugger=False
                        )
                        self.last_engine_content = engine_info
                    
                    print(f"检查完成，等待 {self.check_interval} 秒后进行下一次检查...")
                    time.sleep(self.check_interval)
                    
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(f"检查过程中出错: {str(e)}")
                    print("60秒后重试...")
                    time.sleep(60)
                    
        except KeyboardInterrupt:
            print("\n收到退出信号，正在停止监控...")
            self.send_notification(
                "荣耀快应用调试器监控服务",
                "🔔 监控服务已停止运行",
                is_debugger=True
            )
            self.send_notification(
                "荣耀快应用引擎监控服务",
                "🔔 监控服务已停止运行",
                is_debugger=False
            )

    def is_duplicate_feature(self, new_text, existing_features):
        """检查是否是重复的功能"""
        # 检查完全相同
        if new_text in existing_features:
            print(f"跳过重复功能: {new_text}")
            return True
        
        # 检查包含关系（只检查完全包含的情况）
        for feature in existing_features:
            if new_text == feature:  # 完全相同
                print(f"跳过重复功能: {new_text}")
                return True
        
        return False

if __name__ == "__main__":
    # 飞书机器人 webhook 地址
    debugger_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/3359b367-baf6-44c4-8536-3ebd7aedc03e"  # 调试器机器人
    engine_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/5fe61b9f-a14e-468e-aeb7-72b473f2e6df"  # 引擎机器人
    
    # 创建监控器实例（每5分钟检查一次）
    monitor = HonorMonitor(debugger_webhook_url, engine_webhook_url, check_interval=10)
    
    # 开始监控
    monitor.monitor() 