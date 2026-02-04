from crawler import NovelCrawler
import time

def test_novel_crawler():
    """测试小说爬虫功能"""
    print("开始测试小说爬虫...")
    nc = NovelCrawler()
    
    # 测试起点爬虫
    print("\n--- 测试起点中文网 ---")
    qidian_results = nc.crawl_qidian()
    print(f"起点爬取结果: {len(qidian_results)}条")
    for i, novel in enumerate(qidian_results[:3]):
        print(f"{i+1}. {novel['title']} [{novel['category']}] - {novel['url']}")
    
    time.sleep(2)
    
    # 测试晋江爬虫
    print("\n--- 测试晋江文学城 ---")
    jjwxc_results = nc.crawl_jjwxc()
    print(f"晋江爬取结果: {len(jjwxc_results)}条")
    for i, novel in enumerate(jjwxc_results[:3]):
        print(f"{i+1}. {novel['title']} [{novel['category']}] - {novel['url']}")

if __name__ == "__main__":
    test_novel_crawler()