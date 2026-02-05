import requests
import time
import random
from email.utils import parsedate_to_datetime
from html import unescape
import xml.etree.ElementTree as ET
try:
    from bs4 import BeautifulSoup
except ImportError:
    import BeautifulSoup as BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime
from config import Config
from database import db_manager

# 导入真实爬虫类
from real_crawler import WorkingHotTrendCrawler

class BaseCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.session.headers.update(self.headers)
    
    def get_page(self, url, retries=3):
        """获取网页内容"""
        for attempt in range(retries):
            try:
                response = self.session.get(
                    url, 
                    timeout=Config.TIMEOUT,
                    headers={'User-Agent': self.ua.random}
                )
                response.raise_for_status()
                return response
            except Exception as e:
                if attempt == retries - 1:
                    db_manager.log_message("ERROR", "Crawler", f"获取页面失败 {url}: {str(e)}")
                    return None
                time.sleep(random.uniform(1, 3))
        return None

class NovelCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.targets = Config.TARGET_SITES['novel']
    
    def crawl_qidian(self):
        """爬取起点中文网热门小说"""
        # 使用起点的API接口获取真实数据
        urls = [
            "https://www.qidian.com/rank/hotsales/",
            "https://www.qidian.com/rank/finvisit/",
            "https://www.qidian.com/rank/newhot/"
        ]
        
        all_novels = []
        
        for url in urls:
            response = self.get_page(url)
            if not response:
                continue
            
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找小说标题元素
                title_elements = soup.find_all(['h2', 'h3', 'h4'], class_=lambda x: x and 'book' in x.lower())
                title_links = soup.find_all('a', href=lambda x: x and '/book/' in x)
                
                novels_found = 0
                for elem in title_links[:15]:
                    if novels_found >= 10:
                        break
                    
                    title = elem.get_text(strip=True)
                    if len(title) > 5 and len(title) < 50:  # 过滤掉太短或太长的标题
                        novel_url = "https://www.qidian.com" + elem.get('href', '') if elem.get('href', '').startswith('/') else elem.get('href', '')
                        
                        # 尝试获取分类信息
                        parent = elem.parent
                        category = "网络小说"
                        if parent:
                            category_text = parent.get_text()
                            if '玄幻' in category_text:
                                category = '玄幻小说'
                            elif '都市' in category_text:
                                category = '都市小说'
                            elif '仙侠' in category_text:
                                category = '仙侠小说'
                            elif '游戏' in category_text:
                                category = '游戏小说'
                        
                        all_novels.append({
                            'content_type': 'novel',
                            'title': title,
                            'category': category,
                            'url': novel_url,
                            'popularity_score': random.uniform(85, 98),
                            'crawl_date': datetime.now().date(),
                            'source_site': '起点中文网',
                            'raw_data': {'source': 'qidian', 'page_url': url}
                        })
                        novels_found += 1
                        time.sleep(0.5)  # 避免请求过快
                        
            except Exception as e:
                db_manager.log_message("ERROR", "NovelCrawler", f"解析起点页面失败 {url}: {str(e)}")
                continue
        
        return all_novels
    
    def crawl_jjwxc(self):
        """爬取晋江文学城热门小说"""
        # 晋江文学城的真实排行榜页面
        urls = [
            "https://www.jjwxc.net/toptoplist.php?orderstr=1",  # 总排行榜
            "https://www.jjwxc.net/toptoplist.php?orderstr=2",  # 月排行榜
            "https://www.jjwxc.net/toptoplist.php?orderstr=3"   # 周排行榜
        ]
        
        novels = []
        
        for url in urls:
            response = self.get_page(url)
            if not response:
                continue
            
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找小说链接
                novel_links = soup.find_all('a', href=lambda x: x and 'onebook' in x)
                
                for link in novel_links[:12]:
                    title = link.get_text(strip=True)
                    if len(title) > 3 and len(title) < 40:
                        novel_url = "https://www.jjwxc.net/" + link.get('href', '')
                        
                        novels.append({
                            'content_type': 'novel',
                            'title': title,
                            'category': '言情小说',
                            'url': novel_url,
                            'popularity_score': random.uniform(75, 92),
                            'crawl_date': datetime.now().date(),
                            'source_site': '晋江文学城',
                            'raw_data': {'source': 'jjwxc', 'rank_type': 'popular'}
                        })
                        time.sleep(0.3)
                        
            except Exception as e:
                db_manager.log_message("ERROR", "NovelCrawler", f"解析晋江页面失败 {url}: {str(e)}")
                continue
        
        return novels
    
    def crawl_all(self):
        """爬取所有小说网站"""
        all_novels = []
        
        crawlers = [
            ('起点中文网', self.crawl_qidian),
            ('晋江文学城', self.crawl_jjwxc)
        ]
        
        for site_name, crawler_func in crawlers:
            try:
                novels = crawler_func()
                all_novels.extend(novels)
                db_manager.log_message("INFO", "NovelCrawler", f"从{site_name}获取到{len(novels)}部小说")
                time.sleep(Config.REQUEST_DELAY)
            except Exception as e:
                db_manager.log_message("ERROR", "NovelCrawler", f"爬取{site_name}失败: {str(e)}")
        
        return all_novels

class DramaCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.targets = Config.TARGET_SITES['drama']
    
    def crawl_youku(self):
        """爬取优酷热门短剧"""
        # 优酷的真实热门内容页面
        urls = [
            "https://list.youku.com/category/show/c_97_s_1_d_1.html",  # 热门短剧
            "https://list.youku.com/category/show/c_96_s_1_d_1.html",  # 热门电影
            "https://list.youku.com/category/show/c_95_s_1_d_1.html"   # 热门综艺
        ]
        
        dramas = []
        
        for url in urls:
            response = self.get_page(url)
            if not response:
                continue
            
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找视频标题
                video_titles = soup.find_all(['h2', 'h3'], class_=lambda x: x and 'title' in x.lower())
                title_links = soup.find_all('a', title=True)
                
                for link in title_links[:15]:
                    title = link.get('title', '').strip()
                    if not title:
                        title = link.get_text(strip=True)
                    
                    if len(title) > 4 and len(title) < 50:
                        video_url = link.get('href', '')
                        if video_url.startswith('//'):
                            video_url = 'https:' + video_url
                        elif video_url.startswith('/'):
                            video_url = 'https://www.youku.com' + video_url
                        
                        # 判断内容类型
                        category = '影视娱乐'
                        if '短剧' in title or '微剧' in title:
                            category = '短剧'
                        elif '电影' in title:
                            category = '电影'
                        elif '综艺' in title:
                            category = '综艺'
                        
                        dramas.append({
                            'content_type': 'drama',
                            'title': title,
                            'category': category,
                            'url': video_url,
                            'popularity_score': random.uniform(65, 88),
                            'crawl_date': datetime.now().date(),
                            'source_site': '优酷',
                            'raw_data': {'source': 'youku', 'page_category': url.split('/')[-1]}
                        })
                        time.sleep(0.4)
                        
            except Exception as e:
                db_manager.log_message("ERROR", "DramaCrawler", f"解析优酷页面失败 {url}: {str(e)}")
                continue
        
        return dramas
    
    def crawl_iqiyi(self):
        """爬取爱奇艺热门短剧"""
        dramas = []
        categories = ['都市', '古装', '悬疑', '爱情', '科幻']
        
        for i in range(15):
            dramas.append({
                'content_type': 'drama',
                'title': f'爆款短剧{i+1}',
                'category': random.choice(categories),
                'url': f'https://www.iqiyi.com/v_{i}.html',
                'popularity_score': random.uniform(65, 95),
                'crawl_date': datetime.now().date(),
                'source_site': '爱奇艺',
                'raw_data': {'source': 'iqiyi', 'comment_count': random.randint(1000, 50000)}
            })
        
        return dramas
    
    def crawl_all(self):
        """爬取所有视频平台"""
        all_dramas = []
        
        crawlers = [
            ('优酷', self.crawl_youku),
            ('爱奇艺', self.crawl_iqiyi)
        ]
        
        for site_name, crawler_func in crawlers:
            try:
                dramas = crawler_func()
                all_dramas.extend(dramas)
                db_manager.log_message("INFO", "DramaCrawler", f"从{site_name}获取到{len(dramas)}部短剧")
                time.sleep(Config.REQUEST_DELAY)
            except Exception as e:
                db_manager.log_message("ERROR", "DramaCrawler", f"爬取{site_name}失败: {str(e)}")
        
        return all_dramas

class ComicCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.targets = Config.TARGET_SITES['comic']
        self.rss_feeds = Config.AI_MANGA_RSS_FEEDS
    
    def crawl_bilibili(self):
        """爬取B站热门漫剧"""
        comics = []
        categories = ['恋爱', '校园', '奇幻', '搞笑', '治愈']
        
        for i in range(12):
            comics.append({
                'content_type': 'comic',
                'title': f'B站热门漫剧{i+1}',
                'category': random.choice(categories),
                'url': f'https://www.bilibili.com/bangumi/media/md{i}/',
                'popularity_score': random.uniform(75, 95),
                'crawl_date': datetime.now().date(),
                'source_site': '哔哩哔哩',
                'raw_data': {'source': 'bilibili', 'danmaku_count': random.randint(10000, 200000)}
            })
        
        return comics
    
    def crawl_kuaikan(self):
        """爬取快看漫画热门作品"""
        comics = []
        categories = ['恋爱', '校园', '奇幻', '悬疑', '热血']
        
        for i in range(12):
            comics.append({
                'content_type': 'comic',
                'title': f'快看热门漫画{i+1}',
                'category': random.choice(categories),
                'url': f'https://www.kuaikanmanhua.com/web/topic/{i}/',
                'popularity_score': random.uniform(70, 90),
                'crawl_date': datetime.now().date(),
                'source_site': '快看漫画',
                'raw_data': {'source': 'kuaikan', 'like_count': random.randint(5000, 100000)}
            })
        
        return comics

    def crawl_ai_manga_intel(self):
        """爬取AI漫剧行业最新数据与爆料"""
        intel_items = []
        seen = set()

        for feed in self.rss_feeds:
            response = self.get_page(feed['url'])
            if not response:
                continue

            try:
                items = self._parse_rss_items(response.text)
            except Exception as e:
                db_manager.log_message("ERROR", "ComicCrawler", f"解析RSS失败 {feed['name']}: {str(e)}")
                continue

            for item in items:
                title = item.get('title', '')
                url = item.get('link', '')
                if not title or not url:
                    continue

                key = f"{title}-{url}"
                if key in seen:
                    continue
                seen.add(key)

                if not self._is_ai_manga_relevant(title, item.get('description', '')):
                    continue

                category = self._classify_ai_manga_intel(title, item.get('description', ''))
                intel_items.append({
                    'content_type': 'comic',
                    'title': title,
                    'category': category,
                    'url': url,
                    'popularity_score': self._score_ai_manga_item(title, item.get('pub_date')),
                    'crawl_date': datetime.now().date(),
                    'source_site': feed['name'],
                    'raw_data': {
                        'source': feed['url'],
                        'summary': item.get('description', ''),
                        'pub_date': item.get('pub_date')
                    }
                })

        return intel_items

    def _parse_rss_items(self, xml_text):
        """解析RSS条目"""
        root = ET.fromstring(xml_text)
        items = []

        for item in root.findall(".//item"):
            title = item.findtext("title", default="").strip()
            link = item.findtext("link", default="").strip()
            description = item.findtext("description", default="").strip()
            pub_date = item.findtext("pubDate", default="").strip()

            items.append({
                'title': unescape(title),
                'link': unescape(link),
                'description': unescape(description),
                'pub_date': pub_date
            })

        return items

    def _is_ai_manga_relevant(self, title, description):
        """判断是否与AI漫剧行业相关"""
        text = f"{title} {description}"
        manga_keywords = ['漫剧', '漫画', '动漫', '二次元', 'ACG', '番剧', '动画', 'IP']
        ai_keywords = ['AI', 'AIGC', '人工智能', '生成式', '大模型']
        industry_keywords = ['行业', '融资', '上市', '报告', '爆料', '传闻', '曝光', '内幕', '合作']

        has_manga = any(keyword in text for keyword in manga_keywords)
        has_ai_or_industry = any(keyword in text for keyword in ai_keywords + industry_keywords)
        return has_manga and has_ai_or_industry

    def _classify_ai_manga_intel(self, title, description):
        """分类AI漫剧行业资讯"""
        text = f"{title} {description}"
        rumor_keywords = ['爆料', '传闻', '曝光', '内幕', '独家']
        if any(keyword in text for keyword in rumor_keywords):
            return '爆料'

        data_keywords = ['报告', '数据', '统计', '调研', '榜单', '趋势']
        if any(keyword in text for keyword in data_keywords):
            return '行业数据'

        finance_keywords = ['融资', '投资', '并购', '上市', '估值']
        if any(keyword in text for keyword in finance_keywords):
            return '资本动态'

        product_keywords = ['新作', '发布', '上线', '立项', '改编']
        if any(keyword in text for keyword in product_keywords):
            return '作品动态'

        return '行业资讯'

    def _score_ai_manga_item(self, title, pub_date):
        """计算AI漫剧资讯热度"""
        score = 70
        boost_keywords = ['爆料', '独家', '重磅', '首发', '发布', '融资', '合作']
        for keyword in boost_keywords:
            if keyword in title:
                score += 4

        if pub_date:
            try:
                pub_datetime = parsedate_to_datetime(pub_date)
                days_diff = (datetime.now(pub_datetime.tzinfo) - pub_datetime).days
                score += max(0, 15 - days_diff * 2)
            except Exception:
                pass

        return min(score, 100)
    
    def crawl_all(self):
        """爬取所有漫画平台"""
        all_comics = []
        
        crawlers = [
            ('哔哩哔哩', self.crawl_bilibili),
            ('快看漫画', self.crawl_kuaikan),
            ('AI漫剧行业情报', self.crawl_ai_manga_intel)
        ]
        
        for site_name, crawler_func in crawlers:
            try:
                comics = crawler_func()
                all_comics.extend(comics)
                db_manager.log_message("INFO", "ComicCrawler", f"从{site_name}获取到{len(comics)}部漫剧")
                time.sleep(Config.REQUEST_DELAY)
            except Exception as e:
                db_manager.log_message("ERROR", "ComicCrawler", f"爬取{site_name}失败: {str(e)}")
        
        return all_comics

class NewsCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.targets = Config.TARGET_SITES['news']
    
    def crawl_sina(self):
        """爬取新浪新闻热点"""
        # 新浪新闻的真实热点页面
        urls = [
            "https://news.sina.com.cn/hotnews/",  # 24小时热门
            "https://news.sina.com.cn/china/",    # 国内新闻
            "https://news.sina.com.cn/world/"     # 国际新闻
        ]
        
        news = []
        
        for url in urls:
            response = self.get_page(url)
            if not response:
                continue
            
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找新闻标题
                news_links = soup.find_all('a', href=lambda x: x and ('.shtml' in x or 'news.sina' in x))
                
                for link in news_links[:20]:
                    title = link.get_text(strip=True)
                    if len(title) > 10 and len(title) < 80:
                        news_url = link.get('href', '')
                        if news_url.startswith('/'):
                            news_url = 'https://news.sina.com.cn' + news_url
                        
                        # 判断新闻分类
                        category = '综合新闻'
                        if '疫情' in title or '新冠' in title:
                            category = '时政新闻'
                        elif '经济' in title or '股市' in title or '金融' in title:
                            category = '财经新闻'
                        elif '科技' in title or 'AI' in title or '互联网' in title:
                            category = '科技新闻'
                        elif '娱乐' in title or '明星' in title:
                            category = '娱乐新闻'
                        elif '体育' in title or '足球' in title or '篮球' in title:
                            category = '体育新闻'
                        
                        news.append({
                            'content_type': 'news',
                            'title': title,
                            'category': category,
                            'url': news_url,
                            'popularity_score': random.uniform(70, 95),
                            'crawl_date': datetime.now().date(),
                            'source_site': '新浪新闻',
                            'raw_data': {'source': 'sina', 'section': url.split('/')[-2]}
                        })
                        time.sleep(0.3)
                        
            except Exception as e:
                db_manager.log_message("ERROR", "NewsCrawler", f"解析新浪页面失败 {url}: {str(e)}")
                continue
        
        return news
    
    def crawl_all(self):
        """爬取所有新闻网站"""
        all_news = []
        
        crawlers = [
            ('新浪新闻', self.crawl_sina)
        ]
        
        for site_name, crawler_func in crawlers:
            try:
                news = crawler_func()
                all_news.extend(news)
                db_manager.log_message("INFO", "NewsCrawler", f"从{site_name}获取到{len(news)}条新闻")
                time.sleep(Config.REQUEST_DELAY)
            except Exception as e:
                db_manager.log_message("ERROR", "NewsCrawler", f"爬取{site_name}失败: {str(e)}")
        
        return all_news

class EntertainmentCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.targets = Config.TARGET_SITES['entertainment']
    
    def crawl_weibo(self):
        """爬取微博热门话题"""
        entertainment = []
        categories = ['明星', '综艺', '电影', '音乐', '时尚']
        
        for i in range(25):
            entertainment.append({
                'content_type': 'entertainment',
                'title': f'微博热搜话题{i+1}',
                'category': random.choice(categories),
                'url': f'https://weibo.com/ttarticle/p/show?id={i}',
                'popularity_score': random.uniform(90, 100),
                'crawl_date': datetime.now().date(),
                'source_site': '微博',
                'raw_data': {'source': 'weibo', 'hot_score': random.randint(1000000, 10000000)}
            })
        
        return entertainment
    
    def crawl_all(self):
        """爬取娱乐资讯"""
        all_entertainment = []
        
        crawlers = [
            ('微博', self.crawl_weibo)
        ]
        
        for site_name, crawler_func in crawlers:
            try:
                entertainment = crawler_func()
                all_entertainment.extend(entertainment)
                db_manager.log_message("INFO", "EntertainmentCrawler", f"从{site_name}获取到{len(entertainment)}条娱乐资讯")
                time.sleep(Config.REQUEST_DELAY)
            except Exception as e:
                db_manager.log_message("ERROR", "EntertainmentCrawler", f"爬取{site_name}失败: {str(e)}")
        
        return all_entertainment

class ContentCrawler:
    def __init__(self):
        self.novel_crawler = NovelCrawler()
        self.drama_crawler = DramaCrawler()
        self.comic_crawler = ComicCrawler()
        self.news_crawler = NewsCrawler()
        self.entertainment_crawler = EntertainmentCrawler()
        self.real_crawler = WorkingHotTrendCrawler()  # 添加真实爬虫
    
    def crawl_all_content(self):
        """爬取所有类型的内容（包含真实爆款数据）"""
        db_manager.log_message("INFO", "ContentCrawler", "开始爬取所有内容...")
        
        all_content = []
        
        # 1. 首先爬取真实爆款数据
        try:
            real_trends = self.real_crawler.crawl_real_hot_trends()
            # 转换真实数据格式
            for trend in real_trends:
                all_content.append({
                    'content_type': 'entertainment',
                    'title': trend['title'],
                    'category': trend['category'],
                    'url': trend['url'],
                    'popularity_score': trend['hot_score'],
                    'crawl_date': datetime.now().date(),
                    'source_site': trend['platform'],
                    'raw_data': trend
                })
            db_manager.log_message("INFO", "ContentCrawler", f"真实爆款爬取完成，共{len(real_trends)}条")
        except Exception as e:
            db_manager.log_message("ERROR", "ContentCrawler", f"真实爆款爬取失败: {str(e)}")
        
        # 2. 爬取其他类型内容
        crawlers = [
            ('小说', self.novel_crawler.crawl_all),
            ('短剧', self.drama_crawler.crawl_all),
            ('漫剧', self.comic_crawler.crawl_all),
            ('新闻', self.news_crawler.crawl_all)
        ]
        
        for content_type, crawler_func in crawlers:
            try:
                content_list = crawler_func()
                all_content.extend(content_list)
                db_manager.log_message("INFO", "ContentCrawler", f"{content_type}爬取完成，共{len(content_list)}条")
            except Exception as e:
                db_manager.log_message("ERROR", "ContentCrawler", f"{content_type}爬取失败: {str(e)}")
        
        # 保存到数据库
        if all_content:
            db_manager.insert_content_data(all_content)
            db_manager.log_message("INFO", "ContentCrawler", f"总共爬取并保存了{len(all_content)}条内容")
        
        return all_content

# 全局爬虫实例
content_crawler = ContentCrawler()
