from crawler import BaseCrawler, DramaCrawler, ComicCrawler, NewsCrawler, EntertainmentCrawler
import time
from datetime import datetime

class HotTrendCrawler:
    """爆款趋势专用爬虫"""
    
    def __init__(self):
        self.drama_crawler = DramaCrawler()
        self.comic_crawler = ComicCrawler()
        self.news_crawler = NewsCrawler()
        self.entertainment_crawler = EntertainmentCrawler()
    
    def crawl_hot_trends(self):
        """爬取各行业爆款趋势"""
        print("🚀 开始爬取行业爆款趋势数据...")
        
        hot_trends = {
            'drama': self._get_drama_hot_trends(),
            'comic': self._get_comic_hot_trends(),
            'news': self._get_news_hot_trends(),
            'entertainment': self._get_entertainment_hot_trends()
        }
        
        # 统计总数据量
        total_count = sum(len(items) for items in hot_trends.values())
        print(f"✅ 爬取完成，共获取 {total_count} 条爆款趋势数据")
        
        return hot_trends
    
    def _get_drama_hot_trends(self):
        """获取短剧爆款趋势"""
        print("📺 爬取短剧爆款趋势...")
        dramas = self.drama_crawler.crawl_all()
        
        # 提取爆款特征
        hot_dramas = []
        for drama in dramas:
            if drama['popularity_score'] > 85:  # 高热度作品
                hot_dramas.append({
                    'title': drama['title'],
                    'category': drama['category'],
                    'platform': drama['source_site'],
                    'hot_score': drama['popularity_score'],
                    'url': drama['url'],
                    'trend_type': '爆款短剧'
                })
        
        print(f"   发现 {len(hot_dramas)} 部爆款短剧")
        return hot_dramas
    
    def _get_comic_hot_trends(self):
        """获取漫剧爆款趋势"""
        print("📚 爬取漫剧爆款趋势...")
        comics = self.comic_crawler.crawl_all()
        
        # 提取爆款特征
        hot_comics = []
        for comic in comics:
            if comic['popularity_score'] > 80:  # 高热度作品
                hot_comics.append({
                    'title': comic['title'],
                    'category': comic['category'],
                    'platform': comic['source_site'],
                    'hot_score': comic['popularity_score'],
                    'url': comic['url'],
                    'trend_type': '爆款漫剧'
                })
        
        print(f"   发现 {len(hot_comics)} 部爆款漫剧")
        return hot_comics
    
    def _get_news_hot_trends(self):
        """获取新闻爆款趋势"""
        print("📰 爬取新闻爆款趋势...")
        news = self.news_crawler.crawl_all()
        
        # 提取热点新闻
        hot_news = []
        for item in news:
            if item['popularity_score'] > 90:  # 极高热度
                hot_news.append({
                    'title': item['title'],
                    'category': item['category'],
                    'source': item['source_site'],
                    'hot_score': item['popularity_score'],
                    'url': item['url'],
                    'trend_type': '热点新闻'
                })
        
        print(f"   发现 {len(hot_news)} 条热点新闻")
        return hot_news
    
    def _get_entertainment_hot_trends(self):
        """获取娱乐爆款趋势"""
        print("🎮 爬取娱乐爆款趋势...")
        entertainment = self.entertainment_crawler.crawl_all()
        
        # 提取娱乐热点
        hot_entertainment = []
        for item in entertainment:
            if item['popularity_score'] > 95:  # 超高热度
                hot_entertainment.append({
                    'title': item['title'],
                    'category': item['category'],
                    'platform': item['source_site'],
                    'hot_score': item['popularity_score'],
                    'url': item['url'],
                    'trend_type': '娱乐爆款'
                })
        
        print(f"   发现 {len(hot_entertainment)} 条娱乐爆款")
        return hot_entertainment

def display_hot_trends():
    """显示爆款趋势数据"""
    crawler = HotTrendCrawler()
    trends = crawler.crawl_hot_trends()
    
    print("\n" + "="*60)
    print("🔥 行业爆款趋势报告")
    print("="*60)
    
    # 按类型显示
    for category, items in trends.items():
        if items:
            category_names = {
                'drama': '📺 短剧爆款',
                'comic': '📚 漫剧爆款', 
                'news': '📰 新闻热点',
                'entertainment': '🎮 娱乐爆款'
            }
            
            print(f"\n{category_names[category]} ({len(items)}条)")
            print("-" * 40)
            
            for i, item in enumerate(items[:10], 1):  # 显示前10条
                score_display = "🔥" * int(item['hot_score'] / 20)  # 热度可视化
                print(f"{i:2d}. {item['title']}")
                platform = item.get('platform', item.get('source', '未知'))
                print(f"    分类: {item['category']} | 平台: {platform}")
                print(f"    热度: {item['hot_score']:.1f} {score_display}")
                if item.get('url'):
                    print(f"    链接: {item['url']}")
                print()

if __name__ == "__main__":
    display_hot_trends()