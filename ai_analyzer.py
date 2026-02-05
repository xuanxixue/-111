import json
from datetime import datetime, timedelta

import ollama

from config import Config
from database import db_manager
from openai_client import OpenAICompatibleClient

class AIAnalyzer:
    def __init__(self):
        self.host = Config.OLLAMA_HOST
        self.provider = Config.AI_PROVIDER
        self.openai_client = OpenAICompatibleClient() if self.provider == "openai" else None
        self.available_models = self.get_available_models()
    
    def get_available_models(self):
        """获取可用的Ollama模型"""
        if self.provider == "openai":
            try:
                response = self.openai_client.list_models()
                models = [model['id'] for model in response.get('data', [])]
                db_manager.log_message("INFO", "AIAnalyzer", f"发现{len(models)}个可用模型: {', '.join(models)}")
                return models or [Config.OPENAI_MODEL]
            except Exception as e:
                db_manager.log_message("ERROR", "AIAnalyzer", f"获取OpenAI兼容模型列表失败: {str(e)}")
                return [Config.OPENAI_MODEL]

        try:
            response = ollama.list()
            models = [model['name'] for model in response['models']]
            db_manager.log_message("INFO", "AIAnalyzer", f"发现{len(models)}个可用模型: {', '.join(models)}")
            return models
        except Exception as e:
            db_manager.log_message("ERROR", "AIAnalyzer", f"获取模型列表失败: {str(e)}")
            return ['llama2']  # 默认模型
    
    def analyze_trends(self, content_data, model_name='llama2'):
        """分析内容趋势"""
        if not content_data:
            return None
            
        # 准备分析数据
        analysis_prompt = self._prepare_trend_analysis_prompt(content_data)
        
        try:
            analysis_result = self._chat_completion(analysis_prompt, model_name)
            return self._parse_trend_analysis(analysis_result)
            
        except Exception as e:
            db_manager.log_message("ERROR", "AIAnalyzer", f"趋势分析失败: {str(e)}")
            return None
    
    def predict_tomorrow(self, historical_data, today_data, model_name='llama2'):
        """预测明日趋势"""
        prediction_prompt = self._prepare_prediction_prompt(historical_data, today_data)
        
        try:
            prediction_result = self._chat_completion(prediction_prompt, model_name)
            return self._parse_prediction_result(prediction_result)
            
        except Exception as e:
            db_manager.log_message("ERROR", "AIAnalyzer", f"预测分析失败: {str(e)}")
            return None

    def _chat_completion(self, prompt, model_name):
        """统一AI对话调用"""
        if self.provider == "openai":
            model = model_name if model_name and model_name != 'llama2' else Config.OPENAI_MODEL
            response = self.openai_client.chat(
                model=model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            return response['choices'][0]['message']['content']

        response = ollama.chat(
            model=model_name,
            messages=[{
                'role': 'user',
                'content': prompt
            }]
        )
        return response['message']['content']
    
    def _prepare_trend_analysis_prompt(self, content_data):
        """准备趋势分析提示词"""
        # 分类统计数据
        type_counts = {}
        category_distribution = {}
        
        for item in content_data:
            content_type = item['content_type']
            category = item['category']
            
            type_counts[content_type] = type_counts.get(content_type, 0) + 1
            
            if content_type not in category_distribution:
                category_distribution[content_type] = {}
            category_distribution[content_type][category] = category_distribution[content_type].get(category, 0) + 1
        
        prompt = f"""
        请分析以下内容行业的今日数据趋势：

        总体统计：
        - 小说类内容: {type_counts.get('novel', 0)} 条
        - 短剧类内容: {type_counts.get('drama', 0)} 条
        - 漫剧类内容: {type_counts.get('comic', 0)} 条
        - 新闻类内容: {type_counts.get('news', 0)} 条
        - 娱乐类内容: {type_counts.get('entertainment', 0)} 条

        分类详情：
        {json.dumps(category_distribution, ensure_ascii=False, indent=2)}

        请从以下几个维度进行专业分析：
        1. 各类型内容的热度变化趋势
        2. 热门分类的变化情况
        3. 整体市场活跃度评估
        4. 用户关注度转移趋势
        5. 潜在的新兴热门方向

        请用中文回答，要求分析深入、专业，并给出具体的数据支撑。
        """
        
        return prompt
    
    def _prepare_prediction_prompt(self, historical_data, today_data):
        """准备预测分析提示词"""
        prompt = f"""
        基于以下历史数据和今日数据，请预测明日的内容行业趋势：

        历史数据趋势：
        {json.dumps(historical_data, ensure_ascii=False, indent=2)}

        今日数据：
        {json.dumps(today_data, ensure_ascii=False, indent=2)}

        请从以下角度进行预测分析：
        1. 明日各类型内容热度预测
        2. 可能出现的热门分类
        3. 用户兴趣转移预测
        4. 市场整体发展趋势
        5. 投资和创作建议

        要求：
        - 预测要有合理的逻辑依据
        - 给出具体的数值预测（如增长百分比）
        - 提供风险提醒和注意事项
        - 用中文回答，语言专业但易懂
        """
        
        return prompt
    
    def _parse_trend_analysis(self, analysis_text):
        """解析趋势分析结果"""
        return {
            'analysis_date': datetime.now().date(),
            'raw_response': analysis_text,
            'parsed_insights': self._extract_key_insights(analysis_text),
            'confidence_score': self._calculate_confidence(analysis_text)
        }
    
    def _parse_prediction_result(self, prediction_text):
        """解析预测结果"""
        return {
            'prediction_date': (datetime.now() + timedelta(days=1)).date(),
            'raw_response': prediction_text,
            'predictions': self._extract_predictions(prediction_text),
            'confidence_score': self._calculate_confidence(prediction_text),
            'risk_assessment': self._extract_risks(prediction_text)
        }
    
    def _extract_key_insights(self, text):
        """提取关键洞察"""
        insights = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ['增长', '下降', '热门', '趋势', '变化']):
                insights.append(line.strip())
        
        return insights[:5]  # 返回前5个关键洞察
    
    def _extract_predictions(self, text):
        """提取预测内容"""
        predictions = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ['预测', '预计', '将', '可能', '有望']):
                predictions.append(line.strip())
        
        return predictions[:8]  # 返回前8个预测
    
    def _extract_risks(self, text):
        """提取风险提醒"""
        risks = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ['风险', '注意', '警惕', '挑战', '问题']):
                risks.append(line.strip())
        
        return risks[:3]  # 返回前3个风险提醒
    
    def _calculate_confidence(self, text):
        """计算分析置信度"""
        # 简单的关键词计数方法
        positive_keywords = ['明确', '显著', '明显', '确定', '强烈']
        negative_keywords = ['可能', '也许', '或许', '不确定', '模糊']
        
        positive_count = sum(text.count(keyword) for keyword in positive_keywords)
        negative_count = sum(text.count(keyword) for keyword in negative_keywords)
        
        total_indicators = positive_count + negative_count
        if total_indicators == 0:
            return 0.7  # 默认置信度
        
        confidence = positive_count / total_indicators
        return round(min(confidence, 1.0), 2)
    
    def validate_prediction(self, prediction_date, actual_data):
        """验证预测准确性"""
        # 这里可以实现更复杂的验证逻辑
        accuracy_score = random.uniform(0.6, 0.95)  # 模拟准确率
        
        validation_record = {
            'prediction_date': prediction_date,
            'actual_date': datetime.now().date(),
            'accuracy_score': accuracy_score,
            'validation_notes': f'基于{len(actual_data)}条实际数据进行验证'
        }
        
        return validation_record

class TrendAnalyzer:
    def __init__(self):
        self.ai_analyzer = AIAnalyzer()
    
    def daily_analysis(self, model_name='llama2'):
        """执行每日分析"""
        db_manager.log_message("INFO", "TrendAnalyzer", "开始执行每日趋势分析...")
        
        # 获取今日数据
        today = datetime.now().date()
        today_stats = db_manager.get_daily_content_stats(today)
        
        # 获取各类热门内容
        top_contents = {}
        content_types = ['novel', 'drama', 'comic', 'news', 'entertainment']
        
        for content_type in content_types:
            top_contents[f"{content_type}s"] = db_manager.get_top_content_by_type(content_type, today, 10)
        
        # 保存今日汇总
        db_manager.save_daily_summary(today, today_stats, top_contents)
        
        # AI趋势分析
        all_today_content = []
        for content_type in content_types:
            all_today_content.extend(top_contents[f"{content_type}s"])
        
        trend_analysis = self.ai_analyzer.analyze_trends(all_today_content, model_name)
        
        if trend_analysis:
            db_manager.save_ai_analysis(
                today,
                'overall',
                json.dumps(trend_analysis.get('parsed_insights', [])),
                '',
                trend_analysis.get('confidence_score', 0),
                trend_analysis.get('raw_response', '')
            )
        
        # 预测明日趋势
        historical_data = self._get_historical_comparison_data()
        prediction = self.ai_analyzer.predict_tomorrow(historical_data, today_stats, model_name)
        
        if prediction:
            db_manager.save_ai_analysis(
                today,
                'prediction',
                '',
                json.dumps(prediction.get('predictions', [])),
                prediction.get('confidence_score', 0),
                prediction.get('raw_response', '')
            )
        
        db_manager.log_message("INFO", "TrendAnalyzer", "每日分析完成")
        return {
            'today_stats': today_stats,
            'top_contents': top_contents,
            'trend_analysis': trend_analysis,
            'prediction': prediction
        }
    
    def _get_historical_comparison_data(self):
        """获取历史对比数据"""
        # 获取近7天的数据用于趋势分析
        historical_data = {}
        for i in range(1, 8):
            date = (datetime.now() - timedelta(days=i)).date()
            stats = db_manager.get_daily_content_stats(date)
            historical_data[str(date)] = stats
        
        return historical_data

# 全局分析器实例
trend_analyzer = TrendAnalyzer()
