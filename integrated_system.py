from smart_manga_crawler import MangaIndustryCrawler, HardwareMonitor
from database import db_manager
from ai_analyzer import AIAnalyzer
import json
import time
from datetime import datetime

class IntegratedMangaSystem:
    """集成化的漫剧行业分析系统"""
    
    def __init__(self):
        self.crawler = MangaIndustryCrawler()
        self.monitor = HardwareMonitor()
        self.ai_analyzer = AIAnalyzer()
        self.system_status = {
            'last_run': None,
            'total_crawled': 0,
            'hardware_health': 'good',
            'ai_model_status': 'ready'
        }
    
    def run_complete_analysis(self, industry_keyword="漫剧"):
        """运行完整的行业分析流程"""
        print("🎯 启动漫剧行业完整分析系统")
        print("=" * 60)
        
        # 1. 硬件状态检查
        print("1️⃣ 检查系统硬件状态...")
        hardware_metrics = self.monitor.get_system_metrics()
        self._display_hardware_status(hardware_metrics)
        
        performance_issues = self.monitor.diagnose_performance_issues(hardware_metrics)
        if performance_issues:
            print(f"⚠️ 发现性能问题: {', '.join(performance_issues)}")
            self.system_status['hardware_health'] = 'warning'
        else:
            print("✅ 硬件状态良好")
            self.system_status['hardware_health'] = 'good'
        
        # 2. 动态目标发现
        print("\n2️⃣ 发现行业相关目标...")
        targets = self.crawler.discover_industry_targets(industry_keyword)
        print(f"   发现 {len(targets)} 个可爬取目标")
        
        # 3. 智能爬取
        print("\n3️⃣ 执行智能爬取...")
        manga_data = self.crawler.crawl_manga_content(targets)
        print(f"   成功获取 {len(manga_data)} 条漫剧数据")
        
        # 4. 数据存储
        print("\n4️⃣ 存储数据到数据库...")
        self._save_manga_data(manga_data)
        
        # 5. AI分析
        print("\n5️⃣ 执行AI趋势分析...")
        analysis_results = self._perform_ai_analysis(manga_data)
        
        # 6. 生成报告
        print("\n6️⃣ 生成分析报告...")
        report = self._generate_comprehensive_report(manga_data, analysis_results, hardware_metrics)
        
        # 更新系统状态
        self.system_status.update({
            'last_run': datetime.now().isoformat(),
            'total_crawled': len(manga_data),
            'report_generated': True
        })
        
        print("\n" + "=" * 60)
        print("✅ 漫剧行业分析完成！")
        return report
    
    def _display_hardware_status(self, metrics):
        """显示硬件状态"""
        print(f"   CPU使用率: {metrics['cpu_percent']:.1f}%")
        print(f"   内存使用率: {metrics['memory_percent']:.1f}%")
        print(f"   磁盘使用率: {metrics['disk_usage']:.1f}%")
        
        if 'gpu_name' in metrics:
            print(f"   GPU型号: {metrics['gpu_name']}")
            print(f"   GPU负载: {metrics['gpu_load']:.1f}%")
            print(f"   GPU温度: {metrics['gpu_temperature']:.1f}°C")
    
    def _save_manga_data(self, manga_data):
        """保存漫剧数据到数据库"""
        db_records = []
        for manga in manga_data:
            db_records.append({
                'content_type': 'comic',
                'title': manga['title'],
                'category': manga['category'],
                'url': manga['url'],
                'popularity_score': manga['popularity_score'],
                'crawl_date': datetime.now().date(),
                'source_site': manga['platform'],
                'raw_data': manga
            })
        
        if db_records:
            db_manager.insert_content_data(db_records)
            print(f"   ✅ 成功保存 {len(db_records)} 条记录到数据库")
    
    def _perform_ai_analysis(self, manga_data):
        """执行AI分析"""
        try:
            # 准备分析数据
            analysis_input = {
                'total_count': len(manga_data),
                'categories': {},
                'avg_popularity': sum(m['popularity_score'] for m in manga_data) / len(manga_data) if manga_data else 0,
                'top_works': sorted(manga_data, key=lambda x: x['popularity_score'], reverse=True)[:5]
            }
            
            # 统计分类分布
            for manga in manga_data:
                category = manga['category']
                analysis_input['categories'][category] = analysis_input['categories'].get(category, 0) + 1
            
            # 调用AI分析
            analysis_result = self.ai_analyzer.analyze_trends([{'content_type': 'comic', **m} for m in manga_data])
            
            return {
                'basic_stats': analysis_input,
                'ai_insights': analysis_result
            }
            
        except Exception as e:
            print(f"   ❌ AI分析失败: {str(e)}")
            return {'error': str(e)}
    
    def _generate_comprehensive_report(self, manga_data, analysis_results, hardware_metrics):
        """生成综合分析报告"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'system_status': self.system_status,
            'hardware_metrics': hardware_metrics,
            'crawling_results': {
                'total_found': len(manga_data),
                'by_category': {},
                'top_popular': []
            },
            'ai_analysis': analysis_results
        }
        
        # 分类统计
        for manga in manga_data:
            category = manga['category']
            report['crawling_results']['by_category'][category] = \
                report['crawling_results']['by_category'].get(category, 0) + 1
        
        # 热门作品
        top_works = sorted(manga_data, key=lambda x: x['popularity_score'], reverse=True)[:10]
        report['crawling_results']['top_popular'] = [
            {
                'rank': i+1,
                'title': manga['title'],
                'category': manga['category'],
                'popularity': manga['popularity_score'],
                'platform': manga['platform']
            }
            for i, manga in enumerate(top_works)
        ]
        
        return report
    
    def get_system_dashboard(self):
        """获取系统仪表盘信息"""
        return {
            'status': self.system_status,
            'hardware': self.monitor.get_system_metrics(),
            'recent_activity': self._get_recent_activity()
        }
    
    def _get_recent_activity(self):
        """获取最近活动记录"""
        # 从数据库获取最近的爬取记录
        try:
            from datetime import datetime, timedelta
            recent_date = (datetime.now() - timedelta(days=1)).date()
            stats = db_manager.get_daily_content_stats(recent_date)
            return {
                'date': str(recent_date),
                'comic_count': stats.get('comic', 0),
                'total_count': stats.get('total', 0)
            }
        except:
            return {'error': '无法获取活动数据'}

def interactive_system():
    """交互式系统界面"""
    system = IntegratedMangaSystem()
    
    while True:
        print("\n" + "="*50)
        print("🎮 漫剧行业智能分析系统")
        print("="*50)
        print("1. 执行完整行业分析")
        print("2. 查看系统状态")
        print("3. 查看硬件监控")
        print("4. 获取最新报告")
        print("5. 退出系统")
        
        choice = input("\n请选择操作 (1-5): ").strip()
        
        if choice == '1':
            keyword = input("请输入行业关键词 (默认: 漫剧): ").strip() or "漫剧"
            report = system.run_complete_analysis(keyword)
            
            # 保存报告
            with open(f'manga_analysis_report_{int(time.time())}.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print("✅ 分析报告已保存")
            
        elif choice == '2':
            dashboard = system.get_system_dashboard()
            print(json.dumps(dashboard, ensure_ascii=False, indent=2))
            
        elif choice == '3':
            hardware = system.monitor.get_system_metrics()
            print("🖥️ 硬件监控信息:")
            for key, value in hardware.items():
                print(f"   {key}: {value}")
                
        elif choice == '4':
            # 显示最新的分析结果
            print("📋 最新分析摘要:")
            # 这里可以从数据库获取最新数据
            
        elif choice == '5':
            print("👋 系统退出")
            break
            
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    # 可以选择交互模式或直接运行
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_system()
    else:
        # 直接运行分析
        system = IntegratedMangaSystem()
        report = system.run_complete_analysis("漫剧")
        
        # 输出关键信息
        print("\n📊 关键统计:")
        if 'crawling_results' in report:
            results = report['crawling_results']
            print(f"   总爬取数量: {results['total_found']}")
            print("   分类分布:")
            for category, count in results['by_category'].items():
                print(f"     {category}: {count}部")
            
            print("\n   🔥 热门作品Top5:")
            for work in results['top_popular'][:5]:
                print(f"     {work['rank']}. {work['title']} [{work['category']}] - 热度: {work['popularity']}")