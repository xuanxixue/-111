from database import db_manager
from datetime import datetime

def show_crawled_data():
    """显示爬取的真实数据"""
    today = datetime.now().date()
    
    # 获取统计数据
    stats = db_manager.get_daily_content_stats(today)
    print("=== 今日真实数据统计 ===")
    for content_type, count in stats.items():
        if content_type != 'total':
            type_names = {
                'novel': '小说',
                'drama': '短剧', 
                'comic': '漫剧',
                'news': '新闻',
                'entertainment': '娱乐'
            }
            print(f"{type_names.get(content_type, content_type)}: {count}条")
    
    print(f"\n总计: {stats.get('total', 0)}条数据\n")
    
    # 显示各类热门内容
    content_types = ['novel', 'drama', 'comic', 'news', 'entertainment']
    type_names = {
        'novel': '小说',
        'drama': '短剧',
        'comic': '漫剧', 
        'news': '新闻',
        'entertainment': '娱乐'
    }
    
    for ctype in content_types:
        print(f"=== 热门{type_names[ctype]}TOP5 ===")
        top_content = db_manager.get_top_content_by_type(ctype, today, 5)
        for i, content in enumerate(top_content, 1):
            print(f"{i}. {content['title']} [{content['category']}] - 热度:{content['popularity_score']:.1f}")
        print()

if __name__ == "__main__":
    show_crawled_data()