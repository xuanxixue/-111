import sqlite3
import os
import json
from datetime import datetime
from config import Config

class DatabaseManager:
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self.init_database()
    
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path, **Config.DATABASE_CONFIG)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 创建内容数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_type TEXT NOT NULL,  -- novel, drama, comic, news, entertainment
                title TEXT NOT NULL,
                category TEXT,
                url TEXT,
                popularity_score REAL DEFAULT 0,
                crawl_date DATE NOT NULL,
                source_site TEXT,
                raw_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建AI分析结果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_date DATE NOT NULL,
                content_type TEXT NOT NULL,
                trend_summary TEXT,
                prediction_result TEXT,
                confidence_score REAL,
                raw_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建每日汇总表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                summary_date DATE NOT NULL UNIQUE,
                novel_count INTEGER DEFAULT 0,
                drama_count INTEGER DEFAULT 0,
                comic_count INTEGER DEFAULT 0,
                news_count INTEGER DEFAULT 0,
                entertainment_count INTEGER DEFAULT 0,
                total_count INTEGER DEFAULT 0,
                top_novels TEXT,  -- JSON格式存储热门小说
                top_dramas TEXT,  -- JSON格式存储热门短剧
                top_comics TEXT,  -- JSON格式存储热门漫剧
                top_news TEXT,    -- JSON格式存储热门新闻
                top_entertainment TEXT,  -- JSON格式存储热门娱乐内容
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建预测验证表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prediction_validation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_date DATE NOT NULL,
                actual_date DATE NOT NULL,
                content_type TEXT NOT NULL,
                predicted_trend TEXT,
                actual_trend TEXT,
                accuracy_score REAL,
                validation_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建系统日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_level TEXT NOT NULL,
                module TEXT,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        self.log_message("INFO", "Database", "数据库初始化完成")
    
    def insert_content_data(self, content_list):
        """插入内容数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for content in content_list:
            cursor.execute('''
                INSERT INTO content_data 
                (content_type, title, category, url, popularity_score, crawl_date, source_site, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                content['content_type'],
                content['title'],
                content.get('category', ''),
                content.get('url', ''),
                content.get('popularity_score', 0),
                content.get('crawl_date', datetime.now().date()),
                content.get('source_site', ''),
                json.dumps(content.get('raw_data', {}))
            ))
        
        conn.commit()
        conn.close()
    
    def get_daily_content_stats(self, date=None):
        """获取指定日期的内容统计"""
        if date is None:
            date = datetime.now().date()
            
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT content_type, COUNT(*) as count
            FROM content_data 
            WHERE crawl_date = ?
            GROUP BY content_type
        ''', (date,))
        
        results = cursor.fetchall()
        conn.close()
        
        stats = {
            'novel': 0, 'drama': 0, 'comic': 0, 'news': 0, 'entertainment': 0
        }
        
        for row in results:
            stats[row['content_type']] = row['count']
        
        stats['total'] = sum(stats.values())
        return stats
    
    def get_top_content_by_type(self, content_type, date=None, limit=10):
        """获取指定类型和日期的热门内容"""
        if date is None:
            date = datetime.now().date()
            
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, category, popularity_score, url
            FROM content_data 
            WHERE content_type = ? AND crawl_date = ?
            ORDER BY popularity_score DESC
            LIMIT ?
        ''', (content_type, date, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def save_daily_summary(self, summary_date, content_stats, top_contents):
        """保存每日汇总数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 删除已存在的同日期记录
        cursor.execute('DELETE FROM daily_summary WHERE summary_date = ?', (summary_date,))
        
        # 插入新的汇总记录
        cursor.execute('''
            INSERT INTO daily_summary 
            (summary_date, novel_count, drama_count, comic_count, news_count, entertainment_count, 
             total_count, top_novels, top_dramas, top_comics, top_news, top_entertainment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            summary_date,
            content_stats.get('novel', 0),
            content_stats.get('drama', 0),
            content_stats.get('comic', 0),
            content_stats.get('news', 0),
            content_stats.get('entertainment', 0),
            content_stats.get('total', 0),
            json.dumps(top_contents.get('novels', [])),
            json.dumps(top_contents.get('dramas', [])),
            json.dumps(top_contents.get('comics', [])),
            json.dumps(top_contents.get('news', [])),
            json.dumps(top_contents.get('entertainment', []))
        ))
        
        conn.commit()
        conn.close()
    
    def save_ai_analysis(self, analysis_date, content_type, trend_summary, prediction_result, confidence_score, raw_response):
        """保存AI分析结果"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ai_analysis 
            (analysis_date, content_type, trend_summary, prediction_result, confidence_score, raw_response)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (analysis_date, content_type, trend_summary, prediction_result, confidence_score, raw_response))
        
        conn.commit()
        conn.close()
    
    def get_recent_analyses(self, limit=10):
        """获取最近的AI分析结果"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM ai_analysis 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def log_message(self, level, module, message):
        """记录系统日志"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_logs (log_level, module, message)
            VALUES (?, ?, ?)
        ''', (level, module, message))
        
        conn.commit()
        conn.close()

# 全局数据库实例
db_manager = DatabaseManager()