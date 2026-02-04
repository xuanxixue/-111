# 内容趋势分析与预测系统

一个集成了网络爬虫、AI分析和预测功能的智能化内容趋势分析平台。

## 🌟 系统特性

- **多源数据采集**: 自动从小说、短剧、漫剧、新闻、娱乐等多个渠道获取热门内容
- **AI智能分析**: 集成Ollama本地AI模型进行深度趋势分析
- **实时预测**: 基于历史数据和当前趋势预测明日市场动向
- **可视化展示**: 美观的高科技风格Web界面，实时数据图表
- **自动化运维**: 支持定时任务和自动数据更新

## 🏗️ 系统架构

```
内容趋势分析系统
├── 爬虫模块 (crawler.py)
│   ├── 小说爬虫
│   ├── 短剧爬虫
│   ├── 漫剧爬虫
│   ├── 新闻爬虫
│   └── 娱乐爬虫
├── AI分析引擎 (ai_analyzer.py)
│   ├── 趋势分析
│   ├── 预测建模
│   └── 结果验证
├── 数据库管理 (database.py)
│   ├── SQLite存储
│   ├── 数据统计
│   └── 日志记录
├── Web后端 (app.py)
│   ├── Flask API
│   ├── 定时任务
│   └── 数据接口
└── 前端界面 (templates/index.html)
    ├── 仪表盘
    ├── 详情分析
    └── 数据可视化
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装Ollama (如果未安装)
# 访问 https://ollama.ai 下载安装
```

### 2. 启动Ollama服务

```bash
# 启动Ollama服务
ollama serve

# 拉取AI模型 (可选)
ollama pull llama2
ollama pull mistral
```

### 3. 启动系统

```bash
# 方法1: 使用启动脚本
python start.py

# 方法2: 直接运行
python app.py
```

### 4. 访问系统

打开浏览器访问: http://localhost:5000

## 🔧 配置说明

### 系统配置 (config.py)

```python
# 爬虫配置
REQUEST_DELAY = 1      # 请求间隔(秒)
TIMEOUT = 10           # 超时时间(秒)
MAX_RETRIES = 3        # 最大重试次数

# Ollama配置
OLLAMA_HOST = "http://localhost:11434"

# 定时任务
SCHEDULE_TIME = "02:00"  # 每日更新时间
```

### 目标网站配置

```python
TARGET_SITES = {
    'novel': ['https://www.qidian.com/', ...],
    'drama': ['https://www.youku.com/', ...],
    'comic': ['https://www.bilibili.com/', ...],
    'news': ['https://www.sina.com.cn/', ...],
    'entertainment': ['https://www.weibo.com/', ...]
}
```

## 📊 功能模块

### 1. 数据采集模块
- 支持多个内容平台的自动化爬取
- 智能反爬虫策略
- 数据清洗和标准化

### 2. AI分析模块
- 集成多种Ollama本地模型
- 实时趋势分析
- 智能预测算法
- 准确性验证机制

### 3. 数据可视化
- 交互式图表展示
- 实时数据更新
- 多维度数据分析
- 响应式界面设计

### 4. 系统管理
- 定时任务调度
- 日志监控
- 性能优化
- 错误处理

## 🎨 界面特色

- **高科技风格**: 深色主题配霓虹色彩
- **响应式设计**: 适配各种设备屏幕
- **实时交互**: 动态数据更新和图表渲染
- **直观展示**: 清晰的数据可视化呈现

## 🔍 API接口

### 主要API端点

```
GET  /api/dashboard/stats        # 获取仪表盘统计数据
GET  /api/content/top/{type}     # 获取热门内容排行
GET  /api/analysis/recent        # 获取最新AI分析
POST /api/crawler/update         # 触发数据更新
POST /api/analysis/predict       # 运行AI预测
GET  /api/charts/trends          # 获取趋势图表数据
GET  /api/models/list            # 获取可用AI模型
```

## 📈 数据分析维度

### 内容类型分析
- 小说类: 玄幻、都市、仙侠、游戏等分类热度
- 短剧类: 都市、古装、悬疑、爱情等题材趋势
- 漫剧类: 恋爱、校园、奇幻、搞笑等风格分析
- 新闻类: 时政、财经、科技、娱乐等领域关注度
- 娱乐类: 明星、综艺、电影、音乐等话题热度

### 趋势指标
- 内容数量变化
- 热度评分走势
- 用户关注度迁移
- 市场活跃度指数
- 预测准确率追踪

## ⚙️ 高级功能

### 1. 模型切换
支持在多种Ollama模型间切换，根据不同需求选择合适的AI模型。

### 2. 定制化分析
可根据特定需求定制分析维度和指标。

### 3. 数据导出
支持将分析结果导出为Excel、JSON等格式。

### 4. 预警机制
可设置阈值预警，及时发现异常趋势。

## 🛠️ 开发指南

### 项目结构
```
项目根目录/
├── app.py              # 主应用入口
├── start.py            # 启动脚本
├── config.py           # 系统配置
├── database.py         # 数据库管理
├── crawler.py          # 爬虫模块
├── ai_analyzer.py      # AI分析引擎
├── requirements.txt    # 依赖包列表
├── templates/          # HTML模板
│   └── index.html
├── static/             # 静态资源
│   └── js/
│       └── main.js
├── data/               # 数据库存储
└── logs/               # 系统日志
```

### 扩展开发
1. 添加新的内容源爬虫
2. 集成更多AI分析模型
3. 开发移动端应用
4. 实现数据API开放

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进系统！

## 📄 许可证

本项目采用MIT许可证。

## 📞 技术支持

如有问题，请联系技术支持团队。