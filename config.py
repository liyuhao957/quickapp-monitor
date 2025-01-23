# 监控配置
MONITOR_CONFIG = {
    # 荣耀快应用监控配置
    'honor': {
        'name': '荣耀快应用监控',
        'debugger_webhook': "https://open.feishu.cn/open-apis/bot/v2/hook/3359b367-baf6-44c4-8536-3ebd7aedc03e",
        'engine_webhook': "https://open.feishu.cn/open-apis/bot/v2/hook/5fe61b9f-a14e-468e-aeb7-72b473f2e6df",
        'check_interval': 300  # 5分钟
    },
    
    # 华为快应用加载器监控配置
    'huawei_loader': {
        'name': '华为快应用加载器监控',
        'url': "https://developer.huawei.com/consumer/cn/doc/Tools-Library/quickapp-ide-download-0000001101172926",
        'webhook': "https://open.feishu.cn/open-apis/bot/v2/hook/b5d78e2d-502d-42c7-81d2-48eebf43224e",
        'check_interval': 300  # 5分钟
    },
    
    # 华为快应用版本说明监控配置
    'huawei_version': {
        'name': '华为快应用版本监控',
        'url': "https://developer.huawei.com/consumer/cn/doc/quickApp-Guides/quickapp-version-updates-0000001079803874",
        'webhook': "https://open.feishu.cn/open-apis/bot/v2/hook/1a11a0f0-b246-423c-909f-5ebbbbf4e2f4",
        'check_interval': 300  # 5分钟
    }
}

# 进程管理配置
PROCESS_CONFIG = {
    'health_check_interval': 60,  # 1分钟检查一次进程健康
    'restart_on_crash': True,     # 进程崩溃时自动重启
    'max_restarts': 3,            # 最大重启次数
    'restart_delay': 5            # 重启前等待时间（秒）
} 