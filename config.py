import os
from datetime import datetime

class Config:
    # 基础配置
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'content_analyzer.db')
    LOG_PATH = os.path.join(BASE_DIR, 'logs')
    
    # 爬虫配置
    REQUEST_DELAY = 1  # 请求间隔（秒）
    TIMEOUT = 10       # 超时时间（秒）
    MAX_RETRIES = 3    # 最大重试次数
    
    # Ollama配置
    OLLAMA_HOST = "http://localhost:11434"
    
    # 数据库配置
    DATABASE_CONFIG = {
        'timeout': 30,
        'check_same_thread': False
    }
    
    # 定时任务配置
    SCHEDULE_TIME = "02:00"  # 每天凌晨2点执行数据更新
    
    # 网站目标配置
    TARGET_SITES = {
        'novel': [
            'https://www.qidian.com/',
            'https://www.jjwxc.net/',
            'https://www.xxsy.net/'
        ],
        'drama': [
            'https://www.youku.com/',
            'https://www.iqiyi.com/',
            'https://v.qq.com/'
        ],
        'comic': [
            'https://www.bilibili.com/',
            'https://www.kuaikanmanhua.com/',
            'https://www.manhuatai.com/'
        ],
        'news': [
            'https://www.sina.com.cn/',
            'https://www.163.com/',
            'https://www.sohu.com/'
        ],
        'entertainment': [
            'https://www.weibo.com/',
            'https://www.douban.com/',
            'https://www.zhihu.com/'
        ]
    }
    
    @staticmethod
    def init_directories():
        """初始化必要的目录"""
        dirs = [
            os.path.join(Config.BASE_DIR, 'data'),
            os.path.join(Config.BASE_DIR, 'logs'),
            os.path.join(Config.BASE_DIR, 'templates'),
            os.path.join(Config.BASE_DIR, 'static')
        ]
        
        for directory in dirs:
            if not os.path.exists(directory):
                os.makedirs(directory)
                
    @staticmethod
    def get_current_time():
        """获取当前时间字符串"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')