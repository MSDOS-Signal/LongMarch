#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI大模型应用配置文件
"""

# 服务端配置
SERVER_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": True,
    "reload": True
}

# 客户端配置
CLIENT_CONFIG = {
    "server_url": "http://localhost:8000",
    "window_title": "AI大模型助手 - 科技版",
    "window_size": "1200x800",
    "min_size": (1000, 700)
}

# UI主题配置
UI_THEME = {
    "colors": {
        'bg_primary': '#0a0a0a',      # 主背景色（深黑）
        'bg_secondary': '#1a1a1a',    # 次背景色（深灰）
        'accent_red': '#ff0040',      # 主红色
        'accent_red_dark': '#cc0033', # 深红色
        'accent_red_light': '#ff3366', # 浅红色
        'text_primary': '#ffffff',    # 主文字色
        'text_secondary': '#cccccc',  # 次文字色
        'text_muted': '#888888',      # 弱化文字色
        'border': '#ff0040',          # 边框色
        'success': '#00ff40',         # 成功色
        'warning': '#ffaa00',         # 警告色
        'error': '#ff4040'            # 错误色
    },
    "fonts": {
        'title': ('Consolas', 24, 'bold'),
        'subtitle': ('Consolas', 12),
        'body': ('Consolas', 11),
        'small': ('Consolas', 10)
    }
}

# 视频配置
VIDEO_CONFIG = {
    "path": "resources/ai_avatar.mp4",
    "width": 400,
    "height": 300,
    "fps": 30
}

# AI模型配置
AI_CONFIG = {
    "timeout": 30,
    "max_retries": 3,
    "default_responses": {
        "你好": "你好！我是AI助手，很高兴为您服务！",
        "你是谁": "我是一个基于大模型的AI助手，专门为您提供智能对话服务。",
        "帮助": "我可以回答各种问题，进行对话交流，并为您提供智能建议。",
        "天气": "抱歉，我无法获取实时天气信息，但我可以为您提供其他帮助。",
        "时间": "我无法获取当前时间，建议您查看系统时间。",
        "再见": "再见！期待下次与您交流！"
    }
}
