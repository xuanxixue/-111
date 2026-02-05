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

    # AI提供方配置 (ollama/openai)
    AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "30"))
    
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

    # AI漫剧行业资讯/爆料RSS源
    AI_MANGA_RSS_FEEDS = [
        {
            'name': 'GoogleNews-漫剧行业',
            'url': 'https://news.google.com/rss/search?q=%E6%BC%AB%E5%89%A7%20%E8%A1%8C%E4%B8%9A&hl=zh-CN&gl=CN&ceid=CN:zh-Hans'
        },
        {
            'name': 'GoogleNews-AI漫画',
            'url': 'https://news.google.com/rss/search?q=AI%20%E6%BC%AB%E7%94%BB%20AIGC&hl=zh-CN&gl=CN&ceid=CN:zh-Hans'
        },
        {
            'name': 'GoogleNews-动漫融资',
            'url': 'https://news.google.com/rss/search?q=%E5%8A%A8%E6%BC%AB%20%E8%9E%8D%E8%B5%84%20%E4%BA%A7%E4%B8%9A&hl=zh-CN&gl=CN&ceid=CN:zh-Hans'
        },
        {
            'name': 'GoogleNews-漫剧爆料',
            'url': 'https://news.google.com/rss/search?q=%E6%BC%AB%E5%89%A7%20%E7%88%86%E6%96%99%20%E4%BC%A0%E9%97%BB&hl=zh-CN&gl=CN&ceid=CN:zh-Hans'
        }
    ]
    
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
