import requests
import time
import json
import re
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse
import whois
from datetime import datetime
import psutil
import GPUtil

class SmartSearchEngine:
    """智能搜索引擎 - 专门针对漫剧行业"""
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self.session.headers.update(self.headers)
        
        # 漫剧行业关键词库
        self.manga_keywords = [
            '漫画', '动漫', '漫剧', '二次元', 'ACG', '连载', '完结',
            '热门漫画', '新番', '人气', '排行榜', '推荐',
            'comic', 'manga', 'anime', 'manhua', 'manhwa'
        ]
        
        # 目标网站池
        self.target_sites = [
            'bilibili.com', 'kuaikanmanhua.com', 'manhuatai.com',
            'qq.com', '163.com', 'sina.com.cn', 'sohu.com',
            'douban.com', 'zhihu.com', 'weibo.com'
        ]
    
    def search_with_engines(self, query, max_results=50):
        """多搜索引擎查询"""
        print(f"🔍 搜索查询: {query}")
        
        all_results = []
        
        # 构造行业相关查询
        industry_queries = [
            query,
            f"{query} 漫画",
            f"{query} 动漫",
            f"{query} 热门",
            f"{query} 排行榜"
        ]
        
        for search_query in industry_queries:
            # 模拟搜索引擎结果（实际应接入真实API）
            engine_results = self._simulate_search_results(search_query)
            all_results.extend(engine_results)
            time.sleep(1)
        
        # 去重和排序
        unique_results = self._deduplicate_results(all_results)
        return sorted(unique_results, key=lambda x: x['relevance'], reverse=True)[:max_results]
    
    def _simulate_search_results(self, query):
        """模拟搜索引擎结果（实际应替换为真实API）"""
        # 这里应该接入真实的搜索引擎API
        # 现在模拟一些漫剧相关内容
        base_urls = [
            "https://www.bilibili.com/read/cv",
            "https://www.kuaikanmanhua.com/web/topic",
            "https://manhua.dmzj.com/info",
            "https://www.manhuatai.com"
        ]
        
        results = []
        for i in range(5):
            url = f"{base_urls[i % len(base_urls)]}/{i+1000}"
            title = f"{query} 热门作品第{i+1}名"
            snippet = f"这是关于{query}的热门漫剧作品，受到了广泛关注..."
            
            results.append({
                'title': title,
                'url': url,
                'snippet': snippet,
                'relevance': 100 - i * 5,
                'source': 'simulated'
            })
        
        return results
    
    def _deduplicate_results(self, results):
        """结果去重"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        return unique_results

class ProtocolChecker:
    """爬虫协议检查器"""
    
    def __init__(self):
        self.robot_parsers = {}
    
    def check_robots_txt(self, url):
        """检查robots.txt协议"""
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            if base_url not in self.robot_parsers:
                rp = RobotFileParser()
                robots_url = urljoin(base_url, '/robots.txt')
                rp.set_url(robots_url)
                rp.read()
                self.robot_parsers[base_url] = rp
            
            # 检查是否允许爬取
            can_fetch = self.robot_parsers[base_url].can_fetch('*', url)
            return {
                'allowed': can_fetch,
                'checked_url': url,
                'robots_url': urljoin(base_url, '/robots.txt')
            }
            
        except Exception as e:
            return {
                'allowed': False,
                'error': str(e),
                'checked_url': url
            }
    
    def check_site_legality(self, url):
        """检查网站合法性"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # 简单的域名检查
            whois_info = whois.whois(domain)
            return {
                'domain': domain,
                'registered': whois_info.registrar is not None,
                'creation_date': str(whois_info.creation_date) if whois_info.creation_date else 'Unknown'
            }
        except Exception as e:
            return {
                'domain': urlparse(url).netloc,
                'error': str(e)
            }

class MangaIndustryCrawler(SmartSearchEngine, ProtocolChecker):
    """漫剧行业专业爬虫"""
    
    def __init__(self):
        SmartSearchEngine.__init__(self)
        ProtocolChecker.__init__(self)
        self.crawled_domains = set()
        self.industry_patterns = {
            'manga_title': r'[\u4e00-\u9fff\w\s\-_\(\)]+(漫画|动漫|漫剧)',
            'popularity_indicator': r'(热门|人气|火爆| trending |hot |popular )',
            'rating_pattern': r'(\d+\.\d+分|\d+万人气|\d+万点击)'
        }
    
    def discover_industry_targets(self, industry_term="漫剧"):
        """发现行业相关目标网站"""
        print(f"🌐 发现{industry_term}相关目标...")
        
        # 搜索行业相关网站
        search_results = self.search_with_engines(industry_term)
        
        valid_targets = []
        for result in search_results:
            url = result['url']
            protocol_check = self.check_robots_txt(url)
            legality_check = self.check_site_legality(url)
            
            if protocol_check['allowed'] and legality_check.get('registered', False):
                valid_targets.append({
                    'url': url,
                    'title': result['title'],
                    'relevance': result['relevance'],
                    'protocol_ok': True,
                    'legal': True
                })
                print(f"   ✅ {url} - 符合爬取条件")
            else:
                print(f"   ❌ {url} - 不符合爬取条件")
        
        return valid_targets
    
    def crawl_manga_content(self, targets):
        """爬取漫剧内容"""
        print("🕷️ 开始爬取漫剧内容...")
        manga_data = []
        
        for target in targets[:10]:  # 限制爬取数量
            try:
                print(f"   爬取: {target['url']}")
                response = self.session.get(target['url'], timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 提取漫剧相关信息
                manga_info = self._extract_manga_info(soup, target['url'])
                if manga_info:
                    manga_info['source_url'] = target['url']
                    manga_info['crawl_time'] = datetime.now().isoformat()
                    manga_data.append(manga_info)
                
                time.sleep(2)  # 避免过于频繁
                
            except Exception as e:
                print(f"   ❌ 爬取失败 {target['url']}: {str(e)}")
                continue
        
        return manga_data
    
    def _extract_manga_info(self, soup, url):
        """提取漫剧信息"""
        try:
            # 尝试多种选择器
            title_selectors = [
                'h1', 'h2', '.title', '.comic-title',
                '[class*="title"]', '[id*="title"]'
            ]
            
            title = None
            for selector in title_selectors:
                elem = soup.select_one(selector)
                if elem:
                    title_text = elem.get_text(strip=True)
                    if len(title_text) > 3 and len(title_text) < 100:
                        title = title_text
                        break
            
            if not title:
                return None
            
            # 提取其他信息
            manga_info = {
                'title': title,
                'category': self._classify_manga_category(title),
                'popularity_score': self._estimate_popularity(soup),
                'platform': urlparse(url).netloc,
                'url': url
            }
            
            return manga_info
            
        except Exception as e:
            return None
    
    def _classify_manga_category(self, title):
        """分类漫剧类型"""
        categories = {
            '恋爱': ['恋爱', '浪漫', '爱情', '恋爱喜剧'],
            '校园': ['校园', '学园', '学生', '青春'],
            '奇幻': ['奇幻', '魔法', '异世界', '玄幻'],
            '搞笑': ['搞笑', '喜剧', '幽默', '欢乐'],
            '热血': ['热血', '战斗', '冒险', '动作'],
            '治愈': ['治愈', '温馨', '日常', '生活']
        }
        
        for category, keywords in categories.items():
            if any(keyword in title for keyword in keywords):
                return category
        
        return '其他'
    
    def _estimate_popularity(self, soup):
        """估算热度分数"""
        # 简单的热度估算逻辑
        text_content = soup.get_text()
        score = 50  # 基础分数
        
        # 根据关键词加分
        popularity_keywords = ['热门', '人气', '火爆', '推荐', '必看']
        for keyword in popularity_keywords:
            if keyword in text_content:
                score += 5
        
        # 根据数字信息加分
        numbers = re.findall(r'\d+', text_content)
        if numbers:
            avg_number = sum(int(n) for n in numbers[:10]) / len(numbers[:10])
            score += min(avg_number / 1000, 20)
        
        return min(score, 100)

class HardwareMonitor:
    """硬件监控系统"""
    
    def __init__(self):
        self.gpu_available = self._check_gpu_availability()
    
    def _check_gpu_availability(self):
        """检查GPU可用性"""
        try:
            gpus = GPUtil.getGPUs()
            return len(gpus) > 0
        except:
            return False
    
    def get_system_metrics(self):
        """获取系统性能指标"""
        metrics = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'timestamp': datetime.now().isoformat()
        }
        
        # GPU信息
        if self.gpu_available:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # 获取第一个GPU
                    metrics.update({
                        'gpu_name': gpu.name,
                        'gpu_load': gpu.load * 100,
                        'gpu_memory_util': gpu.memoryUtil * 100,
                        'gpu_temperature': gpu.temperature
                    })
            except Exception as e:
                metrics['gpu_error'] = str(e)
        
        return metrics
    
    def diagnose_performance_issues(self, metrics):
        """诊断性能问题"""
        issues = []
        
        if metrics['cpu_percent'] > 80:
            issues.append("CPU使用率过高")
        
        if metrics['memory_percent'] > 85:
            issues.append("内存使用率过高")
        
        if metrics.get('gpu_load', 0) > 90:
            issues.append("GPU负载过高")
        
        if metrics['disk_usage'] > 90:
            issues.append("磁盘空间不足")
        
        return issues

def main():
    """主函数 - 演示完整流程"""
    print("🚀 漫剧行业智能爬虫系统启动")
    print("=" * 50)
    
    # 1. 硬件监控
    monitor = HardwareMonitor()
    hardware_metrics = monitor.get_system_metrics()
    print("🖥️ 硬件状态:")
    print(f"   CPU使用率: {hardware_metrics['cpu_percent']}%")
    print(f"   内存使用率: {hardware_metrics['memory_percent']}%")
    if 'gpu_name' in hardware_metrics:
        print(f"   GPU: {hardware_metrics['gpu_name']} (负载: {hardware_metrics['gpu_load']:.1f}%)")
    
    # 2. 行业目标发现
    crawler = MangaIndustryCrawler()
    targets = crawler.discover_industry_targets("漫剧")
    print(f"\n🎯 发现 {len(targets)} 个符合条件的目标网站")
    
    # 3. 爬取内容
    if targets:
        manga_data = crawler.crawl_manga_content(targets)
        print(f"\n📚 成功爬取 {len(manga_data)} 部漫剧信息")
        
        # 显示部分结果
        print("\n🔥 热门漫剧预览:")
        for i, manga in enumerate(manga_data[:5]):
            print(f"   {i+1}. {manga['title']} [{manga['category']}] - 热度: {manga['popularity_score']:.1f}")
    
    # 4. 性能诊断
    issues = monitor.diagnose_performance_issues(hardware_metrics)
    if issues:
        print(f"\n⚠️ 性能警告: {', '.join(issues)}")
    else:
        print("\n✅ 系统运行正常")

if __name__ == "__main__":
    main()