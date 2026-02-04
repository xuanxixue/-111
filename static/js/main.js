class ContentAnalyzerApp {
    constructor() {
        this.currentView = 'dashboard';
        this.currentModel = 'llama2';
        this.trendsChart = null;
        this.distributionChart = null;
        this.initialize();
    }

    initialize() {
        this.setupEventListeners();
        this.updateDateTime();
        this.loadDashboardData();
        this.loadAvailableModels();
        
        // 设置定时更新时间显示
        setInterval(() => this.updateDateTime(), 1000);
    }

    setupEventListeners() {
        // 导航链接
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = link.getAttribute('data-target');
                this.switchView(target);
            });
        });

        // 原始数据管理按钮
        document.getElementById('refresh-raw-data')?.addEventListener('click', () => {
            this.refreshRawData();
        });
        
        document.getElementById('analyze-pending')?.addEventListener('click', () => {
            this.analyzePendingData();
        });
        
        // 数据筛选
        document.getElementById('data-type-filter')?.addEventListener('change', () => {
            this.filterRawData();
        });
        
        document.getElementById('date-filter')?.addEventListener('change', () => {
            this.filterRawData();
        });
        
        // 爆款趋势按钮
        document.getElementById('refresh-hot-trends')?.addEventListener('click', () => {
            this.refreshHotTrends();
        });
        
        document.getElementById('export-hot-report')?.addEventListener('click', () => {
            this.exportHotReport();
        });

        // 模型选择
        document.getElementById('model-selector').addEventListener('change', (e) => {
            this.currentModel = e.target.value;
        });

        // 更新数据按钮
        document.getElementById('update-data-btn').addEventListener('click', () => {
            this.updateData();
        });

        // 运行预测按钮
        document.getElementById('run-prediction-btn').addEventListener('click', () => {
            this.runPrediction();
        });

        // 返回仪表盘按钮
        document.getElementById('back-to-dashboard').addEventListener('click', () => {
            this.switchView('dashboard');
        });

        // 时间周期按钮
        document.querySelectorAll('.period-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.period-btn').forEach(b => {
                    b.classList.remove('bg-primary', 'bg-opacity-20', 'text-primary');
                    b.classList.add('bg-gray-700', 'text-gray-300');
                });
                e.target.classList.remove('bg-gray-700', 'text-gray-300');
                e.target.classList.add('bg-primary', 'bg-opacity-20', 'text-primary');
                
                const period = e.target.getAttribute('data-period');
                this.loadTrendsChartData(period);
            });
        });

        // 设置按钮
        document.getElementById('settings-btn').addEventListener('click', () => {
            this.showSettings();
        });
    }

    updateDateTime() {
        const now = new Date();
        const dateStr = now.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            weekday: 'long'
        });
        const timeStr = now.toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

        document.getElementById('current-date').textContent = dateStr;
        document.getElementById('current-time').textContent = timeStr;
    }

    async loadDashboardData() {
        try {
            this.showLoading();
            
            // 加载统计数据
            const statsResponse = await fetch('/api/dashboard/stats');
            const statsData = await statsResponse.json();
            
            if (statsData.success) {
                this.updateStatsCards(statsData.data);
            }

            // 加载图表数据
            await this.loadTrendsChartData('7');
            await this.loadDistributionChartData();

            // 加载最新分析
            await this.loadRecentAnalysis();

        } catch (error) {
            console.error('加载仪表盘数据失败:', error);
            this.showError('数据加载失败，请稍后重试');
        } finally {
            this.hideLoading();
        }
    }

    updateStatsCards(data) {
        document.getElementById('hot-novel-count').textContent = data.hot_novel_count;
        document.getElementById('hot-drama-count').textContent = data.hot_drama_count;
        document.getElementById('hot-comic-count').textContent = data.hot_comic_count;
        document.getElementById('prediction-accuracy').textContent = data.prediction_accuracy + '%';
        
        // 更新趋势箭头颜色和数值
        this.updateTrendIndicator('novel-trend', data.novel_trend);
        this.updateTrendIndicator('drama-trend', data.drama_trend);
        this.updateTrendIndicator('comic-trend', data.comic_trend);
        document.getElementById('accuracy-trend').textContent = '+' + data.accuracy_trend + '%';
    }

    updateTrendIndicator(elementId, value) {
        const element = document.getElementById(elementId);
        const absValue = Math.abs(value);
        const isPositive = value >= 0;
        
        element.textContent = (isPositive ? '+' : '') + value + '%';
        element.className = isPositive 
            ? 'text-green-400 flex items-center text-sm'
            : 'text-red-400 flex items-center text-sm';
    }

    async loadTrendsChartData(period) {
        try {
            const response = await fetch(`/api/charts/trends?days=${period}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderTrendsChart(data.data);
            }
        } catch (error) {
            console.error('加载趋势图表数据失败:', error);
        }
    }

    renderTrendsChart(chartData) {
        const ctx = document.getElementById('trends-chart').getContext('2d');
        
        if (this.trendsChart) {
            this.trendsChart.destroy();
        }

        this.trendsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.dates,
                datasets: [
                    {
                        label: '小说',
                        data: chartData.novel_counts,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: '短剧',
                        data: chartData.drama_counts,
                        borderColor: '#8b5cf6',
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: '漫剧',
                        data: chartData.comic_counts,
                        borderColor: '#ec4899',
                        backgroundColor: 'rgba(236, 72, 153, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: '新闻',
                        data: chartData.news_counts,
                        borderColor: '#00f3ff',
                        backgroundColor: 'rgba(0, 243, 255, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: '娱乐',
                        data: chartData.entertainment_counts,
                        borderColor: '#bf00ff',
                        backgroundColor: 'rgba(191, 0, 255, 0.1)',
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#e2e8f0'
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    }
                }
            }
        });
    }

    async loadDistributionChartData() {
        try {
            const response = await fetch('/api/dashboard/stats');
            const data = await response.json();
            
            if (data.success) {
                this.renderDistributionChart(data.data);
            }
        } catch (error) {
            console.error('加载分布图表数据失败:', error);
        }
    }

    renderDistributionChart(statsData) {
        const ctx = document.getElementById('distribution-chart').getContext('2d');
        
        if (this.distributionChart) {
            this.distributionChart.destroy();
        }

        this.distributionChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['小说', '短剧', '漫剧', '新闻', '娱乐'],
                datasets: [{
                    data: [
                        statsData.hot_novel_count,
                        statsData.hot_drama_count,
                        statsData.hot_comic_count,
                        statsData.news_count || 0,
                        statsData.entertainment_count || 0
                    ],
                    backgroundColor: [
                        '#3b82f6',
                        '#8b5cf6',
                        '#ec4899',
                        '#00f3ff',
                        '#bf00ff'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#e2e8f0',
                            padding: 20
                        }
                    }
                }
            }
        });
    }

    async loadRecentAnalysis() {
        try {
            const response = await fetch('/api/analysis/recent?limit=5');
            const data = await response.json();
            
            if (data.success) {
                this.displayRecentAnalysis(data.data);
            }
        } catch (error) {
            console.error('加载分析数据失败:', error);
        }
    }

    displayRecentAnalysis(analyses) {
        const container = document.getElementById('recent-analysis');
        container.innerHTML = '';

        if (analyses.length === 0) {
            container.innerHTML = '<p class="text-gray-400 text-center py-8">暂无分析数据</p>';
            return;
        }

        analyses.forEach(analysis => {
            const analysisElement = document.createElement('div');
            analysisElement.className = 'bg-gray-800 bg-opacity-50 rounded-lg p-4 border border-gray-700';
            
            let trendSummary = '';
            if (analysis.trend_summary && Array.isArray(analysis.trend_summary)) {
                trendSummary = analysis.trend_summary.slice(0, 2).join('<br>');
            }
            
            let predictionResult = '';
            if (analysis.prediction_result && Array.isArray(analysis.prediction_result)) {
                predictionResult = analysis.prediction_result.slice(0, 2).join('<br>');
            }

            analysisElement.innerHTML = `
                <div class="flex items-start justify-between mb-3">
                    <div>
                        <h4 class="font-medium text-white chinese-text">${analysis.content_type === 'overall' ? '综合分析' : '预测分析'}</h4>
                        <p class="text-sm text-gray-400 chinese-text">${analysis.analysis_date}</p>
                    </div>
                    <span class="px-2 py-1 text-xs bg-green-500 bg-opacity-20 text-green-400 rounded">
                        置信度: ${(analysis.confidence_score * 100).toFixed(1)}%
                    </span>
                </div>
                ${trendSummary ? `<div class="text-sm text-gray-300 mb-2 chinese-text"><strong>趋势分析:</strong><br>${trendSummary}</div>` : ''}
                ${predictionResult ? `<div class="text-sm text-gray-300 chinese-text"><strong>预测结果:</strong><br>${predictionResult}</div>` : ''}
            `;
            
            container.appendChild(analysisElement);
        });
    }

    async loadAvailableModels() {
        try {
            const response = await fetch('/api/models/list');
            const data = await response.json();
            
            if (data.success) {
                const selector = document.getElementById('model-selector');
                selector.innerHTML = '';
                
                data.data.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model;
                    option.textContent = model;
                    selector.appendChild(option);
                });
            }
        } catch (error) {
            console.error('加载模型列表失败:', error);
        }
    }

    switchView(viewType) {
        // 更新导航状态
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('bg-primary', 'bg-opacity-20', 'text-primary', 'border-l-4', 'border-primary');
            link.classList.add('hover:bg-gray-700', 'hover:bg-opacity-50');
        });
        
        const activeLink = document.querySelector(`[data-target="${viewType}"]`);
        if (activeLink) {
            activeLink.classList.remove('hover:bg-gray-700', 'hover:bg-opacity-50');
            activeLink.classList.add('bg-primary', 'bg-opacity-20', 'text-primary', 'border-l-4', 'border-primary');
        }

        // 切换视图
        document.getElementById('dashboard-view').classList.add('hidden');
        document.getElementById('raw-data-view').classList.add('hidden');
        document.getElementById('detail-view').classList.add('hidden');

        if (viewType === 'dashboard') {
            document.getElementById('dashboard-view').classList.remove('hidden');
            this.currentView = 'dashboard';
        } else if (viewType === 'raw-data') {
            document.getElementById('raw-data-view').classList.remove('hidden');
            this.currentView = 'raw-data';
            this.loadRawDataView();
        } else if (viewType === 'hot-trends') {
            document.getElementById('hot-trends-view').classList.remove('hidden');
            this.currentView = 'hot-trends';
            this.loadHotTrendsView();
        } else {
            document.getElementById('detail-view').classList.remove('hidden');
            this.currentView = viewType;
            this.loadDetailView(viewType);
        }
    }

    async loadDetailView(contentType) {
        try {
            this.showLoading();
            
            // 更新标题
            const titles = {
                'novel': '小说分析',
                'drama': '短剧分析',
                'comic': '漫剧分析',
                'news': '新闻分析',
                'entertainment': '娱乐分析'
            };
            
            document.getElementById('detail-title').textContent = titles[contentType] || '内容分析';

            // 加载排行榜
            await this.loadRankingData(contentType);

            // 加载趋势分析
            await this.loadContentTypeAnalysis(contentType);

        } catch (error) {
            console.error('加载详情视图失败:', error);
        } finally {
            this.hideLoading();
        }
    }

    async loadRankingData(contentType) {
        try {
            const response = await fetch(`/api/content/top/${contentType}?limit=20`);
            const data = await response.json();
            
            if (data.success) {
                this.displayRanking(data.data, contentType);
            }
        } catch (error) {
            console.error('加载排行榜数据失败:', error);
        }
    }

    displayRanking(items, contentType) {
        const container = document.getElementById('ranking-list');
        container.innerHTML = '';

        if (items.length === 0) {
            container.innerHTML = '<p class="text-gray-400 text-center py-8">暂无数据</p>';
            return;
        }

        items.forEach((item, index) => {
            const rankElement = document.createElement('div');
            rankElement.className = 'flex items-center space-x-3 p-3 bg-gray-800 bg-opacity-30 rounded-lg chinese-text';
            
            const rankColors = ['#fbbf24', '#94a3b8', '#cd7f32'];
            const rankColor = index < 3 ? rankColors[index] : '#64748b';
            
            rankElement.innerHTML = `
                <div class="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm" 
                     style="background-color: ${rankColor}">
                    ${index + 1}
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-white font-medium truncate chinese-text">${item.title}</p>
                    <p class="text-sm text-gray-400 chinese-text">${item.category || '未知分类'}</p>
                </div>
                <div class="text-right">
                    <p class="text-${rankColor}-400 font-medium">${Math.round(item.popularity_score)}</p>
                    <p class="text-xs text-gray-500">热度</p>
                </div>
            `;
            
            container.appendChild(rankElement);
        });
    }

    async loadContentTypeAnalysis(contentType) {
        // 这里可以调用专门的分析API
        const analysisContainer = document.getElementById('trend-analysis');
        analysisContainer.innerHTML = `
            <div class="bg-gray-800 bg-opacity-30 rounded-lg p-4 chinese-text">
                <h4 class="text-white font-medium mb-2">${contentType === 'novel' ? '小说' : 
                                                         contentType === 'drama' ? '短剧' :
                                                         contentType === 'comic' ? '漫剧' :
                                                         contentType === 'news' ? '新闻' : '娱乐'}行业趋势分析</h4>
                <p class="text-gray-400 text-sm">基于AI模型的深度分析显示，该领域呈现出积极的发展态势。建议关注相关投资机会和创作方向。</p>
            </div>
        `;
    }

    async loadRawDataView() {
        try {
            this.showLoading();
            
            // 加载待分析数据统计
            await this.loadPendingDataStats();
            
            // 加载原始数据列表
            await this.loadRawDataList();
            
        } catch (error) {
            console.error('加载原始数据视图失败:', error);
        } finally {
            this.hideLoading();
        }
    }
    
    async loadPendingDataStats() {
        try {
            // 这里应该调用API获取待分析数据统计
            // 暂时使用模拟数据
            const stats = {
                novel: 25,
                drama: 18,
                comic: 12,
                news: 35,
                entertainment: 42
            };
            
            document.getElementById('pending-novel-count').textContent = stats.novel;
            document.getElementById('pending-drama-count').textContent = stats.drama;
            document.getElementById('pending-comic-count').textContent = stats.comic;
            document.getElementById('pending-news-count').textContent = stats.news;
            document.getElementById('pending-entertainment-count').textContent = stats.entertainment;
            
        } catch (error) {
            console.error('加载待分析数据统计失败:', error);
        }
    }
    
    async loadRawDataList() {
        try {
            const typeFilter = document.getElementById('data-type-filter')?.value || 'all';
            const dateFilter = document.getElementById('date-filter')?.value || 'today';
            
            // 调用API获取原始数据
            const response = await fetch(`/api/content/raw?type=${typeFilter}&period=${dateFilter}`);
            const data = await response.json();
            
            if (data.success) {
                this.displayRawDataTable(data.data);
            }
            
        } catch (error) {
            console.error('加载原始数据列表失败:', error);
            // 显示模拟数据用于演示
            this.displayRawDataTable(this.generateMockRawData());
        }
    }
    
    displayRawDataTable(rawData) {
        const container = document.getElementById('raw-data-table');
        container.innerHTML = '';
        
        if (rawData.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8 text-gray-400 chinese-text">
                    <i class="fa fa-database text-4xl mb-4"></i>
                    <p>暂无待分析的原始数据</p>
                </div>
            `;
            return;
        }
        
        // 创建表格
        const table = document.createElement('table');
        table.className = 'w-full text-sm';
        
        table.innerHTML = `
            <thead>
                <tr class="border-b border-gray-700">
                    <th class="text-left py-2 px-3 chinese-text">ID</th>
                    <th class="text-left py-2 px-3 chinese-text">标题</th>
                    <th class="text-left py-2 px-3 chinese-text">类型</th>
                    <th class="text-left py-2 px-3 chinese-text">分类</th>
                    <th class="text-left py-2 px-3 chinese-text">热度</th>
                    <th class="text-left py-2 px-3 chinese-text">来源</th>
                    <th class="text-left py-2 px-3 chinese-text">爬取时间</th>
                    <th class="text-left py-2 px-3 chinese-text">状态</th>
                </tr>
            </thead>
            <tbody id="raw-data-tbody">
            </tbody>
        `;
        
        const tbody = table.querySelector('#raw-data-tbody');
        rawData.forEach(item => {
            const row = document.createElement('tr');
            row.className = 'border-b border-gray-800 hover:bg-gray-800 hover:bg-opacity-30 transition-colors';
            
            // 确定状态显示
            let statusText, statusClass;
            if (item.status === 'analyzed') {
                statusText = '已分析';
                statusClass = 'text-green-400';
            } else if (item.status === 'pending') {
                statusText = '待分析';
                statusClass = 'text-yellow-400';
            } else {
                statusText = '分析中';
                statusClass = 'text-blue-400';
            }
            
            row.innerHTML = `
                <td class="py-2 px-3 text-gray-300">${item.id}</td>
                <td class="py-2 px-3 text-white chinese-text max-w-xs truncate" title="${item.title}">${item.title}</td>
                <td class="py-2 px-3 text-gray-300 chinese-text">${this.getContentTypeName(item.content_type)}</td>
                <td class="py-2 px-3 text-gray-400 chinese-text">${item.category || '未分类'}</td>
                <td class="py-2 px-3">
                    <span class="px-2 py-1 rounded text-xs ${item.popularity_score >= 80 ? 'bg-red-500' : item.popularity_score >= 60 ? 'bg-yellow-500' : 'bg-gray-500'} text-white">
                        ${Math.round(item.popularity_score)}
                    </span>
                </td>
                <td class="py-2 px-3 text-gray-400 chinese-text">${item.source_site}</td>
                <td class="py-2 px-3 text-gray-400 text-xs">${item.crawl_date}</td>
                <td class="py-2 px-3">
                    <span class="px-2 py-1 rounded text-xs ${statusClass}">${statusText}</span>
                </td>
            `;
            
            tbody.appendChild(row);
        });
        
        container.appendChild(table);
    }
    
    getContentTypeName(type) {
        const typeMap = {
            'novel': '小说',
            'drama': '短剧',
            'comic': '漫剧',
            'news': '新闻',
            'entertainment': '娱乐'
        };
        return typeMap[type] || type;
    }
    
    generateMockRawData() {
        // 生成模拟的原始数据用于演示
        const mockData = [];
        const types = ['novel', 'drama', 'comic', 'news', 'entertainment'];
        const sites = {
            'novel': ['起点中文网', '晋江文学城'],
            'drama': ['优酷', '爱奇艺'],
            'comic': ['哔哩哔哩', '快看漫画'],
            'news': ['新浪新闻', '网易新闻'],
            'entertainment': ['微博', '豆瓣']
        };
        
        for (let i = 1; i <= 20; i++) {
            const type = types[Math.floor(Math.random() * types.length)];
            const site = sites[type][Math.floor(Math.random() * sites[type].length)];
            
            mockData.push({
                id: i,
                title: `${this.getContentTypeName(type)}测试数据${i}`,
                content_type: type,
                category: ['玄幻', '都市', '古装', '悬疑', '恋爱'][Math.floor(Math.random() * 5)],
                popularity_score: Math.floor(Math.random() * 100),
                source_site: site,
                crawl_date: new Date().toLocaleDateString('zh-CN'),
                status: ['pending', 'analyzing', 'analyzed'][Math.floor(Math.random() * 3)]
            });
        }
        
        return mockData;
    }
    
    async refreshRawData() {
        this.showMessage('正在刷新原始数据...', 'info');
        await this.loadRawDataView();
        this.showMessage('数据刷新完成', 'success');
    }
    
    async analyzePendingData() {
        try {
            this.showLoading();
            
            const response = await fetch('/api/analysis/process-pending', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: this.currentModel
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showMessage(`成功分析${data.processed_count}条数据`, 'success');
                await this.loadRawDataView(); // 刷新显示
            } else {
                this.showError(data.error || '分析失败');
            }
            
        } catch (error) {
            console.error('分析待处理数据失败:', error);
            this.showError('网络错误，请稍后重试');
        } finally {
            this.hideLoading();
        }
    }
    
    async filterRawData() {
        await this.loadRawDataList();
    }
    
    async updateData() {
        try {
            this.showLoading();
            
            const response = await fetch('/api/crawler/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: this.currentModel
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showMessage('数据更新任务已启动', 'success');
                // 等待一段时间后刷新数据
                setTimeout(() => {
                    if (this.currentView === 'dashboard') {
                        this.loadDashboardData();
                    }
                }, 3000);
            } else {
                this.showError(data.error || '更新失败');
            }
        } catch (error) {
            console.error('更新数据失败:', error);
            this.showError('网络错误，请稍后重试');
        } finally {
            this.hideLoading();
        }
    }

    async runPrediction() {
        try {
            this.showLoading();
            
            const response = await fetch('/api/analysis/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: this.currentModel
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showMessage('AI预测已完成', 'success');
                // 刷新相关数据
                if (this.currentView === 'dashboard') {
                    this.loadDashboardData();
                }
            } else {
                this.showError(data.error || '预测失败');
            }
        } catch (error) {
            console.error('运行预测失败:', error);
            this.showError('网络错误，请稍后重试');
        } finally {
            this.hideLoading();
        }
    }

    showLoading() {
        document.getElementById('loading-overlay').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loading-overlay').classList.add('hidden');
    }

    showMessage(message, type = 'info') {
        // 创建消息提示
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 chinese-text ${
            type === 'success' ? 'bg-green-500' : 
            type === 'error' ? 'bg-red-500' : 'bg-blue-500'
        } text-white`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // 3秒后自动移除
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    showError(message) {
        this.showMessage(message, 'error');
    }

    async loadHotTrendsView() {
        try {
            this.showLoading();
            
            // 加载爆款统计数据
            await this.loadHotTrendsStats();
            
            // 加载各类型爆款列表
            await this.loadHotTrendsLists();
            
        } catch (error) {
            console.error('加载爆款趋势视图失败:', error);
        } finally {
            this.hideLoading();
        }
    }
    
    async loadHotTrendsStats() {
        try {
            // 调用API获取爆款统计数据
            const response = await fetch('/api/hot-trends/stats');
            const data = await response.json();
            
            if (data.success) {
                document.getElementById('hot-drama-count').textContent = data.data.drama_count || 0;
                document.getElementById('hot-comic-count').textContent = data.data.comic_count || 0;
                document.getElementById('hot-news-count').textContent = data.data.news_count || 0;
                document.getElementById('hot-entertainment-count').textContent = data.data.entertainment_count || 0;
            } else {
                // 使用模拟数据
                this.updateHotStatsWithMockData();
            }
            
        } catch (error) {
            console.error('加载爆款统计失败:', error);
            this.updateHotStatsWithMockData();
        }
    }
    
    updateHotStatsWithMockData() {
        // 模拟爆款统计数据
        const mockStats = {
            drama_count: 12,
            comic_count: 25,
            news_count: 8,
            entertainment_count: 32
        };
        
        document.getElementById('hot-drama-count').textContent = mockStats.drama_count;
        document.getElementById('hot-comic-count').textContent = mockStats.comic_count;
        document.getElementById('hot-news-count').textContent = mockStats.news_count;
        document.getElementById('hot-entertainment-count').textContent = mockStats.entertainment_count;
    }
    
    async loadHotTrendsLists() {
        try {
            // 并行加载各类爆款列表
            const [dramaData, comicData, newsData, entertainmentData] = await Promise.all([
                this.fetchHotTrendsByType('drama'),
                this.fetchHotTrendsByType('comic'),
                this.fetchHotTrendsByType('news'),
                this.fetchHotTrendsByType('entertainment')
            ]);
            
            this.displayHotTrendsList('drama', dramaData);
            this.displayHotTrendsList('comic', comicData);
            this.displayHotTrendsList('news', newsData);
            this.displayHotTrendsList('entertainment', entertainmentData);
            
        } catch (error) {
            console.error('加载爆款列表失败:', error);
            // 显示模拟数据
            this.displayMockHotTrends();
        }
    }
    
    async fetchHotTrendsByType(type) {
        try {
            const response = await fetch(`/api/hot-trends/${type}?limit=10`);
            const data = await response.json();
            return data.success ? data.data : [];
        } catch (error) {
            return [];
        }
    }
    
    displayHotTrendsList(type, items) {
        const containerIds = {
            'drama': 'hot-drama-list',
            'comic': 'hot-comic-list',
            'news': 'hot-news-list',
            'entertainment': 'hot-entertainment-list'
        };
        
        const container = document.getElementById(containerIds[type]);
        if (!container) return;
        
        container.innerHTML = '';
        
        if (!items || items.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8 text-gray-400 chinese-text">
                    <i class="fa fa-fire text-3xl mb-2"></i>
                    <p>暂无爆款数据</p>
                </div>
            `;
            return;
        }
        
        items.forEach((item, index) => {
            const trendElement = document.createElement('div');
            trendElement.className = 'flex items-center space-x-3 p-3 bg-gray-800 bg-opacity-30 rounded-lg hover:bg-gray-700 transition-colors';
            
            // 热度等级颜色
            const heatColors = ['#ef4444', '#f97316', '#eab308', '#22c55e'];
            const heatLevel = Math.min(3, Math.floor(item.hot_score / 25));
            const heatColor = heatColors[heatLevel];
            
            trendElement.innerHTML = `
                <div class="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm" 
                     style="background-color: ${heatColor}">
                    ${index + 1}
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-white font-medium truncate chinese-text">${item.title}</p>
                    <div class="flex items-center space-x-2 mt-1">
                        <span class="text-xs px-2 py-1 bg-gray-700 rounded text-gray-300">${item.category}</span>
                        <span class="text-xs text-gray-400">${item.platform || item.source}</span>
                    </div>
                </div>
                <div class="text-right">
                    <div class="flex items-center space-x-1">
                        <span class="text-${heatLevel === 3 ? 'green' : heatLevel === 2 ? 'yellow' : heatLevel === 1 ? 'orange' : 'red'}-400 font-medium">
                            ${item.hot_score.toFixed(1)}
                        </span>
                        <i class="fa fa-fire text-${heatLevel === 3 ? 'green' : heatLevel === 2 ? 'yellow' : heatLevel === 1 ? 'orange' : 'red'}-400"></i>
                    </div>
                    <p class="text-xs text-gray-500">热度指数</p>
                </div>
            `;
            
            container.appendChild(trendElement);
        });
    }
    
    displayMockHotTrends() {
        // 显示模拟的爆款数据用于演示
        const mockData = {
            drama: [
                {title: '爆款短剧·都市爱情故事', category: '都市', platform: '爱奇艺', hot_score: 94.5},
                {title: '古装悬疑·宫斗秘闻', category: '古装', platform: '腾讯视频', hot_score: 92.3},
                {title: '科幻冒险·未来世界', category: '科幻', platform: '优酷', hot_score: 89.7}
            ],
            comic: [
                {title: '恋爱日常·青春物语', category: '恋爱', platform: '快看漫画', hot_score: 96.2},
                {title: '校园搞笑·欢乐时光', category: '搞笑', platform: '哔哩哔哩', hot_score: 93.8},
                {title: '奇幻冒险·异世界', category: '奇幻', platform: '腾讯动漫', hot_score: 91.5}
            ],
            news: [
                {title: '科技前沿·AI技术突破', category: '科技', platform: '新浪新闻', hot_score: 98.1},
                {title: '财经观察·股市动态', category: '财经', platform: '网易新闻', hot_score: 95.3},
                {title: '社会热点·民生关注', category: '社会', platform: '搜狐新闻', hot_score: 92.7}
            ],
            entertainment: [
                {title: '明星八卦·恋情曝光', category: '明星', platform: '微博', hot_score: 99.5},
                {title: '综艺热议·节目争议', category: '综艺', platform: '豆瓣', hot_score: 97.8},
                {title: '音乐榜单·新歌发布', category: '音乐', platform: '网易云音乐', hot_score: 96.4}
            ]
        };
        
        Object.keys(mockData).forEach(type => {
            this.displayHotTrendsList(type, mockData[type]);
        });
    }
    
    async refreshHotTrends() {
        this.showMessage('正在刷新爆款趋势数据...', 'info');
        await this.loadHotTrendsView();
        this.showMessage('爆款数据刷新完成', 'success');
    }
    
    exportHotReport() {
        this.showMessage('正在生成爆款趋势报告...', 'info');
        
        // 模拟报告生成
        setTimeout(() => {
            // 创建下载链接
            const reportData = {
                generated_at: new Date().toISOString(),
                report_type: '爆款趋势分析报告',
                data_summary: '包含短剧、漫剧、新闻、娱乐四个领域的爆款趋势数据'
            };
            
            const blob = new Blob([JSON.stringify(reportData, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `爆款趋势报告_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            this.showMessage('报告已下载完成', 'success');
        }, 1500);
    }

    showSettings() {
        // 这里可以实现设置面板
        alert('设置功能正在开发中...');
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ContentAnalyzerApp();
});