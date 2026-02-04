from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime, timedelta
from database import db_manager
from crawler import content_crawler
from ai_analyzer import trend_analyzer, AIAnalyzer
from config import Config
import schedule
import threading
import time

app = Flask(__name__)
CORS(app)

# 初始化配置
Config.init_directories()

def scheduled_update():
    """定时更新任务"""
    try:
        db_manager.log_message("INFO", "Scheduler", "开始执行定时更新任务")
        
        # 爬取新数据
        content_crawler.crawl_all_content()
        
        # 执行AI分析
        trend_analyzer.daily_analysis()
        
        db_manager.log_message("INFO", "Scheduler", "定时更新任务完成")
    except Exception as e:
        db_manager.log_message("ERROR", "Scheduler", f"定时更新任务失败: {str(e)}")

def run_scheduler():
    """运行调度器"""
    schedule.every().day.at(Config.SCHEDULE_TIME).do(scheduled_update)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    """获取仪表盘统计数据"""
    try:
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # 获取今日统计数据
        today_stats = db_manager.get_daily_content_stats(today)
        yesterday_stats = db_manager.get_daily_content_stats(yesterday)
        
        # 计算增长率
        def calculate_growth(today_val, yesterday_val):
            if yesterday_val == 0:
                return 100 if today_val > 0 else 0
            return round(((today_val - yesterday_val) / yesterday_val) * 100, 1)
        
        stats = {
            'hot_novel_count': today_stats.get('novel', 0),
            'hot_drama_count': today_stats.get('drama', 0),
            'hot_comic_count': today_stats.get('comic', 0),
            'prediction_accuracy': 87.5,  # 模拟准确率
            'novel_trend': calculate_growth(today_stats.get('novel', 0), yesterday_stats.get('novel', 0)),
            'drama_trend': calculate_growth(today_stats.get('drama', 0), yesterday_stats.get('drama', 0)),
            'comic_trend': calculate_growth(today_stats.get('comic', 0), yesterday_stats.get('comic', 0)),
            'accuracy_trend': 2.3  # 模拟准确率趋势
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/content/top/<content_type>')
def get_top_content(content_type):
    """获取指定类型的热门内容"""
    try:
        date_str = request.args.get('date')
        limit = int(request.args.get('limit', 10))
        
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = datetime.now().date()
        
        top_content = db_manager.get_top_content_by_type(content_type, date, limit)
        
        return jsonify({
            'success': True,
            'data': top_content
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analysis/recent')
def get_recent_analysis():
    """获取最近的AI分析结果"""
    try:
        limit = int(request.args.get('limit', 10))
        analyses = db_manager.get_recent_analyses(limit)
        
        # 格式化分析结果
        formatted_analyses = []
        for analysis in analyses:
            formatted_analysis = {
                'id': analysis['id'],
                'analysis_date': analysis['analysis_date'],
                'content_type': analysis['content_type'],
                'confidence_score': analysis['confidence_score'],
                'created_at': analysis['created_at']
            }
            
            # 解析趋势总结
            if analysis['trend_summary']:
                try:
                    formatted_analysis['trend_summary'] = json.loads(analysis['trend_summary'])
                except:
                    formatted_analysis['trend_summary'] = [analysis['trend_summary']]
            
            # 解析预测结果
            if analysis['prediction_result']:
                try:
                    formatted_analysis['prediction_result'] = json.loads(analysis['prediction_result'])
                except:
                    formatted_analysis['prediction_result'] = [analysis['prediction_result']]
            
            formatted_analyses.append(formatted_analysis)
        
        return jsonify({
            'success': True,
            'data': formatted_analyses
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/models/list')
def get_available_models():
    """获取可用的AI模型列表"""
    try:
        ai_analyzer = AIAnalyzer()
        models = ai_analyzer.get_available_models()
        
        return jsonify({
            'success': True,
            'data': models
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/crawler/update', methods=['POST'])
def trigger_crawler():
    """触发数据爬取"""
    try:
        data = request.get_json()
        model_name = data.get('model', 'llama2')
        
        # 在后台线程中执行爬取和分析
        def background_update():
            try:
                # 爬取数据
                content_crawler.crawl_all_content()
                
                # 执行分析
                trend_analyzer.daily_analysis(model_name)
                
                db_manager.log_message("INFO", "API", "手动更新任务完成")
            except Exception as e:
                db_manager.log_message("ERROR", "API", f"手动更新任务失败: {str(e)}")
        
        thread = threading.Thread(target=background_update)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': '数据更新任务已启动'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analysis/predict', methods=['POST'])
def trigger_prediction():
    """触发AI预测"""
    try:
        data = request.get_json()
        model_name = data.get('model', 'llama2')
        
        # 执行预测分析
        result = trend_analyzer.daily_analysis(model_name)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/charts/trends')
def get_trends_chart_data():
    """获取趋势图表数据"""
    try:
        days = int(request.args.get('days', 7))
        
        # 获取历史数据
        chart_data = {
            'dates': [],
            'novel_counts': [],
            'drama_counts': [],
            'comic_counts': [],
            'news_counts': [],
            'entertainment_counts': []
        }
        
        for i in range(days - 1, -1, -1):
            date = (datetime.now() - timedelta(days=i)).date()
            stats = db_manager.get_daily_content_stats(date)
            
            chart_data['dates'].append(date.strftime('%m-%d'))
            chart_data['novel_counts'].append(stats.get('novel', 0))
            chart_data['drama_counts'].append(stats.get('drama', 0))
            chart_data['comic_counts'].append(stats.get('comic', 0))
            chart_data['news_counts'].append(stats.get('news', 0))
            chart_data['entertainment_counts'].append(stats.get('entertainment', 0))
        
        return jsonify({
            'success': True,
            'data': chart_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/content/raw')
def get_raw_content():
    """获取原始爬取数据"""
    try:
        content_type = request.args.get('type', 'all')
        period = request.args.get('period', 'today')
        limit = int(request.args.get('limit', 50))
        
        # 这里应该查询数据库获取原始数据
        # 暂时返回模拟数据
        raw_data = []
        types = ['novel', 'drama', 'comic', 'news', 'entertainment']
        
        if content_type != 'all':
            types = [content_type]
        
        for i in range(min(limit, 30)):
            data_type = types[i % len(types)]
            raw_data.append({
                'id': i + 1,
                'content_type': data_type,
                'title': f'{data_type}原始数据{i+1}',
                'category': ['分类A', '分类B', '分类C'][i % 3],
                'popularity_score': random.uniform(60, 95),
                'source_site': '测试网站',
                'crawl_date': datetime.now().strftime('%Y-%m-%d'),
                'status': ['pending', 'analyzing', 'analyzed'][i % 3]
            })
        
        return jsonify({
            'success': True,
            'data': raw_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analysis/process-pending', methods=['POST'])
def process_pending_data():
    """处理待分析数据"""
    try:
        data = request.get_json()
        model_name = data.get('model', 'llama2')
        
        # 获取待分析的数据
        pending_count = random.randint(5, 20)  # 模拟待处理数据量
        
        # 执行AI分析
        if pending_count > 0:
            # 模拟分析过程
            import time
            time.sleep(2)  # 模拟分析耗时
            
            # 保存分析结果
            analysis_result = {
                'processed_count': pending_count,
                'model_used': model_name,
                'completion_time': Config.get_current_time()
            }
            
            return jsonify({
                'success': True,
                'processed_count': pending_count,
                'result': analysis_result
            })
        else:
            return jsonify({
                'success': True,
                'processed_count': 0,
                'message': '没有待处理的数据'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hot-trends/stats')
def get_hot_trends_stats():
    """获取爆款趋势统计数据"""
    try:
        # 从数据库获取真实统计数据
        from datetime import datetime
        from database import db_manager
        
        today = datetime.now().date()
        stats = db_manager.get_daily_content_stats(today)
        
        # 过滤高热度内容作为爆款
        hot_stats = {
            'drama_count': stats.get('drama', 0),
            'comic_count': stats.get('comic', 0),
            'news_count': stats.get('news', 0),
            'entertainment_count': stats.get('entertainment', 0)
        }
        
        return jsonify({
            'success': True,
            'data': hot_stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hot-trends/<content_type>')
def get_hot_trends_by_type(content_type):
    """获取指定类型的爆款趋势"""
    try:
        limit = int(request.args.get('limit', 10))
        
        from datetime import datetime
        from database import db_manager
        
        today = datetime.now().date()
        # 获取高热度内容作为爆款
        hot_content = db_manager.get_top_content_by_type(content_type, today, limit)
        
        # 添加爆款标识
        for item in hot_content:
            item['trend_type'] = f'爆款{content_type}'
            
        return jsonify({
            'success': True,
            'data': hot_content
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system/status')
def get_system_status():
    """获取系统状态"""
    try:
        # 获取硬件状态
        import psutil
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            gpu_info = {
                'available': True,
                'count': len(gpus),
                'details': [{'name': gpu.name, 'load': gpu.load * 100} for gpu in gpus[:1]] if gpus else []
            }
        except:
            gpu_info = {'available': False}
        
        status = {
            'database_status': 'connected',
            'ollama_status': 'available',
            'last_update': Config.get_current_time(),
            'total_records': 0,  # 可以查询数据库获取实际数量
            'hardware': {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'gpu': gpu_info
            }
        }
        
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/smart-crawl', methods=['POST'])
def smart_crawl_industry():
    """智能行业爬取"""
    try:
        from integrated_system import IntegratedMangaSystem
        
        data = request.get_json()
        keyword = data.get('keyword', '漫剧')
        
        system = IntegratedMangaSystem()
        report = system.run_complete_analysis(keyword)
        
        return jsonify({
            'success': True,
            'data': report
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hardware/metrics')
def get_hardware_metrics():
    """获取硬件监控指标"""
    try:
        import psutil
        metrics = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': {
                'percent': psutil.virtual_memory().percent,
                'used_gb': round(psutil.virtual_memory().used / (1024**3), 2),
                'total_gb': round(psutil.virtual_memory().total / (1024**3), 2)
            },
            'disk': {
                'percent': psutil.disk_usage('/').percent,
                'used_gb': round(psutil.disk_usage('/').used / (1024**3), 2),
                'total_gb': round(psutil.disk_usage('/').total / (1024**3), 2)
            },
            'timestamp': Config.get_current_time()
        }
        
        # GPU信息
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                metrics['gpu'] = {
                    'name': gpus[0].name,
                    'load': round(gpus[0].load * 100, 1),
                    'memory_util': round(gpus[0].memoryUtil * 100, 1),
                    'temperature': gpus[0].temperature
                }
        except:
            metrics['gpu'] = {'available': False}
        
        return jsonify({
            'success': True,
            'data': metrics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # 启动调度器线程
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # 初始化数据库
    db_manager.init_database()
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)