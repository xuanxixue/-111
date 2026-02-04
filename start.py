#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
内容趋势分析与预测系统启动脚本
Content Trend Analysis and Prediction System Startup Script
"""

import os
import sys
import subprocess
from config import Config

def check_dependencies():
    """检查依赖包"""
    print("🔍 检查依赖包...")
    try:
        import flask
        import requests
        import beautifulsoup4
        import ollama
        print("✅ 所有依赖包已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_ollama():
    """检查Ollama服务"""
    print("🔍 检查Ollama服务...")
    try:
        import ollama
        models = ollama.list()
        if models and 'models' in models:
            print(f"✅ Ollama服务正常，发现 {len(models['models'])} 个模型")
            for model in models['models']:
                print(f"   - {model['name']}")
            return True
        else:
            print("⚠️ Ollama服务正常但未发现模型")
            return True
    except Exception as e:
        print(f"❌ Ollama服务不可用: {e}")
        print("请确保Ollama服务已启动: ollama serve")
        return False

def initialize_system():
    """初始化系统"""
    print("🚀 初始化内容趋势分析系统...")
    
    # 初始化目录
    Config.init_directories()
    print("✅ 目录结构初始化完成")
    
    # 初始化数据库
    from database import db_manager
    print("✅ 数据库初始化完成")
    
    return True

def start_system():
    """启动系统"""
    print("\n" + "="*50)
    print("🎯 内容趋势分析与预测系统")
    print("="*50)
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 检查Ollama
    if not check_ollama():
        return False
    
    # 初始化系统
    if not initialize_system():
        return False
    
    print("\n✅ 系统初始化完成!")
    print("\n🌐 启动Web服务...")
    print("   访问地址: http://localhost:5000")
    print("   按 Ctrl+C 停止服务")
    print("="*50)
    
    # 启动Flask应用
    try:
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n\n👋 系统已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = start_system()
    sys.exit(0 if success else 1)