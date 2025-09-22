#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI大模型客户端
基于Tkinter构建的科技感红色主题客户端界面
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import requests
import json
import time
from datetime import datetime
import os
import sys
from PIL import Image, ImageTk
import cv2
from tkinter import font
import markdown
import re

class AIClient:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()
        self.setup_variables()
        self.setup_ui()
        self.setup_video()
        
    @staticmethod
    def resource_path(*relative_parts):
        """在打包环境下解析资源路径 (PyInstaller 支持)。"""
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, *relative_parts)

    def setup_window(self):
        """设置主窗口"""
        self.root.title("长征大模型 - 科技版")
        self.root.geometry("2000x1025")
        self.root.configure(bg='#0a0a0a')
        
        # 设置窗口属性 - 固定尺寸，不可调整大小
        self.root.resizable(False, False)
        
        # 设置窗口属性 - 只显示最小化和关闭按钮
        self.root.attributes('-toolwindow', False)  # 确保不是工具窗口
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 居中显示
        self.center_window()
        
        # 设置窗口图标为 resources/cz.png
        try:
            icon_path = self.resource_path("resources", "cz.png")
            if os.path.exists(icon_path):
                self.icon_image = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(False, self.icon_image)
        except Exception:
            # 忽略图标设置失败，继续运行
            pass
        
    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = 2000
        height = 1025
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def on_closing(self):
        """窗口关闭时的处理"""
        # 停止视频播放
        if hasattr(self, 'video_running') and self.video_running:
            self.stop_video()
        
        # 关闭窗口
        self.root.destroy()
        
    def setup_styles(self):
        """设置样式"""
        self.style = ttk.Style()
        
        # 配置颜色主题
        self.colors = {
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
        }
        
        # 配置ttk样式
        self.style.theme_use('clam')
        
        # 配置按钮样式
        self.style.configure('Red.TButton',
                           background=self.colors['accent_red'],
                           foreground=self.colors['text_primary'],
                           borderwidth=0,
                           focuscolor='none',
                           font=('Microsoft YaHei UI', 11, 'bold'))
        
        self.style.map('Red.TButton',
                      background=[('active', self.colors['accent_red_dark']),
                                ('pressed', self.colors['accent_red_light'])])
        
        # 配置输入框样式
        self.style.configure('Red.TEntry',
                           fieldbackground=self.colors['bg_secondary'],
                           foreground=self.colors['text_primary'],
                           borderwidth=2,
                           relief='solid',
                           insertcolor=self.colors['accent_red'],
                           font=('Microsoft YaHei UI', 12))
        
        # 配置标签样式
        self.style.configure('Title.TLabel',
                           background=self.colors['bg_primary'],
                           foreground=self.colors['accent_red'],
                           font=('Microsoft YaHei UI', 18, 'bold'))
        
        self.style.configure('Subtitle.TLabel',
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_secondary'],
                           font=('Microsoft YaHei UI', 12))
        
    def setup_variables(self):
        """设置变量"""
        self.server_url = "http://localhost:8001"
        self.is_connected = False
        self.conversation_history = []
        self.video_running = False
        self.typing_active = False
        self.current_typing_text = ""
        self.typing_position = 0
        
        # 思考中状态相关变量
        self.thinking_active = False
        self.thinking_dots = 0
        self.thinking_message_id = None
        self.thinking_icons = ["🤔", "💭", "🧠", "⚡"]
        self.thinking_icon_index = 0
        
    def setup_ui(self):
        """设置用户界面"""
        # 主容器
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 标题区域
        self.create_header(main_frame)
        
        # 内容区域
        content_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        content_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # 左侧视频区域
        self.create_video_section(content_frame)
        
        # 右侧聊天区域
        self.create_chat_section(content_frame)
        
        # 底部状态栏
        self.create_status_bar(main_frame)
        
        # 添加科技感装饰
        self.add_tech_decorations(main_frame)
        
    def create_header(self, parent):
        """创建标题区域"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        header_frame.pack(fill='x', pady=(0, 20))
        
        # 主标题
        title_label = tk.Label(header_frame,
                             text="长征大模型",
                             font=('Microsoft YaHei UI', 28, 'bold'),
                             fg=self.colors['accent_red'],
                             bg=self.colors['bg_primary'])
        title_label.pack(side='left')
        
        # 添加版本信息
        version_label = tk.Label(header_frame,
                               text="v1.0.0",
                               font=('Microsoft YaHei UI', 11),
                               fg=self.colors['text_muted'],
                               bg=self.colors['bg_primary'])
        version_label.pack(side='left', padx=(10, 0))
        
        # 连接状态指示器
        self.status_indicator = tk.Label(header_frame,
                                       text="●",
                                       font=('Microsoft YaHei UI', 18),
                                       fg=self.colors['error'],
                                       bg=self.colors['bg_primary'])
        self.status_indicator.pack(side='right', padx=(0, 10))
        
        self.status_label = tk.Label(header_frame,
                                   text="未连接",
                                   font=('Microsoft YaHei UI', 13),
                                   fg=self.colors['text_secondary'],
                                   bg=self.colors['bg_primary'])
        self.status_label.pack(side='right')
        
    def create_video_section(self, parent):
        """创建视频区域"""
        video_frame = tk.LabelFrame(parent,
                                  text="长征AI形象",
                                  font=('Microsoft YaHei UI', 14, 'bold'),
                                  fg=self.colors['accent_red'],
                                  bg=self.colors['bg_primary'],
                                  relief='solid',
                                  bd=2)
        video_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # 视频显示区域
        self.video_label = tk.Label(video_frame,
                                  text="视频加载中...",
                                  font=('Consolas', 14),
                                  fg=self.colors['text_secondary'],
                                  bg=self.colors['bg_secondary'],
                                  width=80,
                                  height=35)
        self.video_label.pack(padx=10, pady=10, fill='both', expand=True)
        
        # 视频状态显示
        self.video_status_label = tk.Label(video_frame,
                                          text="自动播放中...",
                                          font=('Microsoft YaHei UI', 11),
                                          fg=self.colors['success'],
                                          bg=self.colors['bg_primary'])
        self.video_status_label.pack(pady=(0, 10))
        
    def create_chat_section(self, parent):
        """创建聊天区域"""
        chat_frame = tk.LabelFrame(parent,
                                 text="长征智能对话",
                                 font=('Microsoft YaHei UI', 14, 'bold'),
                                 fg=self.colors['accent_red'],
                                 bg=self.colors['bg_primary'],
                                 relief='solid',
                                 bd=2)
        chat_frame.pack(side='right', fill='both', expand=True)
        
        # 聊天历史显示区域
        self.chat_display = scrolledtext.ScrolledText(chat_frame,
                                                    font=('Microsoft YaHei UI', 12),
                                                    bg=self.colors['bg_secondary'],
                                                    fg=self.colors['text_primary'],
                                                    insertbackground=self.colors['accent_red'],
                                                    selectbackground=self.colors['accent_red'],
                                                    selectforeground=self.colors['text_primary'],
                                                    wrap='word',
                                                    state='disabled',
                                                    height=15,
                                                    relief='flat',
                                                    bd=0,
                                                    padx=15,
                                                    pady=15)
        self.chat_display.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 输入区域
        input_frame = tk.Frame(chat_frame, bg=self.colors['bg_primary'])
        input_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # 输入框
        self.input_entry = ttk.Entry(input_frame,
                                   style='Red.TEntry',
                                   font=('Microsoft YaHei UI', 12),
                                   width=50)
        self.input_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.input_entry.bind('<Return>', self.send_message)
        self.input_entry.bind('<KeyPress>', self.on_input_change)
        
        # 添加输入提示
        self.input_placeholder = "向长征AI提问... (按回车发送)"
        self.input_entry.insert(0, self.input_placeholder)
        self.input_entry.config(foreground=self.colors['text_muted'])
        self.input_entry.bind('<FocusIn>', self.on_input_focus_in)
        self.input_entry.bind('<FocusOut>', self.on_input_focus_out)
        self.input_entry.bind('<Button-1>', self.on_input_click)
        self.input_entry.bind('<KeyPress>', self.on_input_key_press)
        
        # 发送按钮
        self.send_button = ttk.Button(input_frame,
                                    text="发送",
                                    style='Red.TButton',
                                    command=self.send_message)
        self.send_button.pack(side='right')
        
        # 清空按钮
        self.clear_button = ttk.Button(input_frame,
                                     text="清空",
                                     style='Red.TButton',
                                     command=self.clear_chat)
        self.clear_button.pack(side='right', padx=(0, 10))
        
    def create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], height=30)
        status_frame.pack(fill='x', pady=(10, 0))
        status_frame.pack_propagate(False)
        
        self.status_text = tk.Label(status_frame,
                                  text="长征AI就绪",
                                  font=('Microsoft YaHei UI', 11),
                                  fg=self.colors['text_secondary'],
                                  bg=self.colors['bg_secondary'])
        self.status_text.pack(side='left', padx=10, pady=5)
        
        # 连接测试按钮
        test_button = ttk.Button(status_frame,
                               text="测试连接",
                               style='Red.TButton',
                               command=self.test_connection)
        test_button.pack(side='right', padx=10, pady=5)
        
    def setup_video(self):
        """设置视频播放"""
        self.video_path = self.resource_path("resources", "ai_avatar.mp4")
        self.cap = None
        self.video_thread = None
        
        # 检查视频文件是否存在
        if os.path.exists(self.video_path):
            self.status_text.config(text=f"视频文件已找到: {self.video_path}")
            # 自动开始播放视频
            self.start_video()
        else:
            self.status_text.config(text="警告: 视频文件未找到")
            
            
    def start_video(self):
        """开始播放视频"""
        if not os.path.exists(self.video_path):
            self.video_status_label.config(text="视频文件不存在", fg=self.colors['error'])
            return
            
        try:
            self.cap = cv2.VideoCapture(self.video_path)
            self.video_running = True
            
            # 启动视频播放线程
            self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
            self.video_thread.start()
            
            self.video_status_label.config(text="自动播放中...", fg=self.colors['success'])
            self.status_text.config(text="视频自动播放中...")
            
        except Exception as e:
            self.video_status_label.config(text=f"播放失败: {str(e)}", fg=self.colors['error'])
            self.status_text.config(text=f"视频播放失败: {str(e)}")
            
    def stop_video(self):
        """停止视频播放"""
        self.video_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.video_label.config(image='', text="视频已停止")
        self.video_status_label.config(text="已停止", fg=self.colors['text_muted'])
        self.status_text.config(text="视频已停止")
        
    def video_loop(self):
        """视频播放循环"""
        while self.video_running and self.cap:
            ret, frame = self.cap.read()
            if not ret:
                # 视频播放完毕，重新开始循环
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
                
            # 获取视频标签的实际尺寸
            label_width = self.video_label.winfo_width()
            label_height = self.video_label.winfo_height()
            
            # 如果标签还没有初始化尺寸，使用默认值
            if label_width <= 1 or label_height <= 1:
                label_width = 1000
                label_height = 750
            
            # 计算保持宽高比的缩放尺寸
            frame_height, frame_width = frame.shape[:2]
            aspect_ratio = frame_width / frame_height
            
            # 根据标签尺寸计算最佳显示尺寸
            if label_width / label_height > aspect_ratio:
                # 标签更宽，以高度为准
                new_height = label_height
                new_width = int(new_height * aspect_ratio)
            else:
                # 标签更高，以宽度为准
                new_width = label_width
                new_height = int(new_width / aspect_ratio)
            
            # 确保尺寸不为0
            new_width = max(1, new_width)
            new_height = max(1, new_height)
            
            # 调整帧大小，保持宽高比
            frame = cv2.resize(frame, (new_width, new_height))
            
            # 转换颜色格式
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 转换为PIL图像
            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image)
            
            # 更新显示
            self.video_label.config(image=photo, text="")
            self.video_label.image = photo  # 保持引用
            
            time.sleep(0.03)  # 控制帧率
            
    def test_connection(self):
        """测试服务器连接"""
        def test():
            try:
                response = requests.get(f"{self.server_url}/health", timeout=10)
                if response.status_code == 200:
                    self.is_connected = True
                    self.status_indicator.config(fg=self.colors['success'])
                    self.status_label.config(text="已连接", fg=self.colors['success'])
                    self.status_text.config(text="服务器连接正常")
                else:
                    raise Exception("服务器响应异常")
            except Exception as e:
                self.is_connected = False
                self.status_indicator.config(fg=self.colors['error'])
                self.status_label.config(text="连接失败", fg=self.colors['error'])
                self.status_text.config(text=f"连接失败: {str(e)}")
                
        threading.Thread(target=test, daemon=True).start()
        
    def send_message(self, event=None):
        """发送消息"""
        message = self.input_entry.get().strip()
        
        # 检查是否是占位符文本
        if not message or message == self.input_placeholder:
            return
            
        if not self.is_connected:
            messagebox.showwarning("警告", "请先连接服务器！")
            return
            
        # 清空输入框并恢复占位符
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, self.input_placeholder)
        self.input_entry.config(foreground=self.colors['text_muted'])
        
        # 显示用户消息
        self.add_message_to_chat("用户", message, "user")
        
        # 发送到服务器
        self.get_ai_response(message)
        
    def get_ai_response(self, message):
        """获取AI响应"""
        def request_response():
            try:
                # 显示思考中状态
                self.root.after(0, self.start_thinking)
                self.root.after(0, lambda: self.status_text.config(text="🤔 长征AI正在思考中..."))
                
                response = requests.post(
                    f"{self.server_url}/chat",
                    json={"message": message, "user_id": "default"},
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    ai_response = data.get("response", "抱歉，我无法理解您的问题。")
                    
                    # 停止思考中状态
                    self.root.after(0, self.stop_thinking)
                    
                    # 显示AI响应
                    self.root.after(0, lambda: self.add_message_to_chat("长征AI", ai_response, "ai"))
                    self.root.after(0, lambda: self.status_text.config(text="✅ 长征AI就绪"))
                else:
                    raise Exception(f"服务器错误: {response.status_code}")
                    
            except Exception as e:
                # 停止思考中状态
                self.root.after(0, self.stop_thinking)
                
                error_msg = f"请求失败: {str(e)}"
                self.root.after(0, lambda: self.add_message_to_chat("系统", error_msg, "system"))
                self.root.after(0, lambda: self.status_text.config(text="❌ 请求失败"))
                
        threading.Thread(target=request_response, daemon=True).start()
        
    def add_message_to_chat(self, sender, message, msg_type):
        """添加消息到聊天显示区域"""
        self.chat_display.config(state='normal')
        
        # 获取当前时间
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 根据消息类型设置颜色
        if msg_type == "user":
            color = self.colors['accent_red']
            prefix = "👤"
        elif msg_type == "ai":
            color = self.colors['success']
            prefix = "🤖"
        else:
            color = self.colors['warning']
            prefix = "⚠️"
            
        # 插入消息头
        self.chat_display.insert(tk.END, f"[{timestamp}] {prefix} {sender}:\n", f"{msg_type}_header")
        
        # 配置标签样式
        self.chat_display.tag_configure(f"{msg_type}_header", foreground=color, font=('Microsoft YaHei UI', 11, 'bold'))
        
        # 如果是AI消息，使用逐字输出效果
        if msg_type == "ai":
            self.start_typing_effect(message)
        else:
            # 用户消息直接显示
            self.chat_display.insert(tk.END, f"{message}\n\n", f"{msg_type}_body")
            self.chat_display.tag_configure(f"{msg_type}_body", foreground=self.colors['text_primary'], font=('Microsoft YaHei UI', 12))
            # 滚动到底部
            self.chat_display.see(tk.END)
            self.chat_display.config(state='disabled')
    
    def start_typing_effect(self, message):
        """开始逐字输出效果"""
        self.typing_active = True
        self.current_typing_text = message
        self.typing_position = 0
        
        # 确保聊天显示区域处于normal状态
        self.chat_display.config(state='normal')
        
        # 创建AI消息的标签
        self.chat_display.tag_configure("ai_body", foreground=self.colors['text_primary'], font=('Microsoft YaHei UI', 12))
        self.chat_display.tag_configure("ai_typing", foreground=self.colors['accent_red'], font=('Microsoft YaHei UI', 12, 'bold'))
        
        # Markdown格式标签
        self.chat_display.tag_configure("ai_bold", foreground=self.colors['accent_red'], font=('Microsoft YaHei UI', 12, 'bold'))
        self.chat_display.tag_configure("ai_heading_1", foreground=self.colors['accent_red'], font=('Microsoft YaHei UI', 16, 'bold'))
        self.chat_display.tag_configure("ai_heading_2", foreground=self.colors['accent_red'], font=('Microsoft YaHei UI', 15, 'bold'))
        self.chat_display.tag_configure("ai_heading_3", foreground=self.colors['accent_red'], font=('Microsoft YaHei UI', 14, 'bold'))
        self.chat_display.tag_configure("ai_list", foreground=self.colors['text_primary'], font=('Microsoft YaHei UI', 12))
        
        # 思考中状态标签
        self.chat_display.tag_configure("ai_thinking", foreground=self.colors['accent_red'], font=('Microsoft YaHei UI', 12, 'italic'))
        self.chat_display.tag_configure("ai_sender", foreground=self.colors['accent_red'], font=('Microsoft YaHei UI', 12, 'bold'))
        
        # 思考中状态指示器标签
        self.chat_display.tag_configure("thinking_indicator", foreground=self.colors['accent_red'], font=('Microsoft YaHei UI', 10, 'bold'))
        
        # 开始逐字输出
        self.type_next_character()
    
    def type_next_character(self):
        """逐字输出下一个字符"""
        if not self.typing_active or self.typing_position >= len(self.current_typing_text):
            self.typing_active = False
            # 添加换行
            self.chat_display.insert(tk.END, "\n\n", "ai_body")
            self.chat_display.see(tk.END)
            # 输出完成后设置为disabled状态
            self.chat_display.config(state='disabled')
            return
        
        # 获取下一个字符
        char = self.current_typing_text[self.typing_position]
        
        # 检查Markdown格式
        if char == '*' and self.typing_position < len(self.current_typing_text) - 1:
            # 检查是否是粗体标记 **text**
            if self.current_typing_text[self.typing_position + 1] == '*':
                # 找到粗体文本的结束位置
                end_pos = self.current_typing_text.find('**', self.typing_position + 2)
                if end_pos != -1:
                    # 提取粗体文本
                    bold_text = self.current_typing_text[self.typing_position + 2:end_pos]
                    # 插入粗体文本
                    self.chat_display.insert(tk.END, bold_text, "ai_bold")
                    # 跳过整个粗体标记
                    self.typing_position = end_pos + 2
                    self.chat_display.see(tk.END)
                    delay = 30
                    self.root.after(delay, self.type_next_character)
                    return
        
        elif char == '#' and (self.typing_position == 0 or self.current_typing_text[self.typing_position - 1] == '\n'):
            # 检查是否是标题
            level = 0
            pos = self.typing_position
            while pos < len(self.current_typing_text) and self.current_typing_text[pos] == '#':
                level += 1
                pos += 1
            
            if level > 0 and pos < len(self.current_typing_text) and self.current_typing_text[pos] == ' ':
                # 找到标题文本的结束位置
                end_pos = self.current_typing_text.find('\n', pos)
                if end_pos == -1:
                    end_pos = len(self.current_typing_text)
                
                # 提取标题文本
                title_text = self.current_typing_text[pos + 1:end_pos]
                # 插入标题文本
                self.chat_display.insert(tk.END, title_text, f"ai_heading_{level}")
                # 跳过整个标题
                self.typing_position = end_pos
                self.chat_display.see(tk.END)
                delay = 50
                self.root.after(delay, self.type_next_character)
                return
        
        elif char == '-' and (self.typing_position == 0 or self.current_typing_text[self.typing_position - 1] == '\n'):
            # 检查是否是列表项
            if self.typing_position + 1 < len(self.current_typing_text) and self.current_typing_text[self.typing_position + 1] == ' ':
                # 找到列表项的结束位置
                end_pos = self.current_typing_text.find('\n', self.typing_position + 2)
                if end_pos == -1:
                    end_pos = len(self.current_typing_text)
                
                # 提取列表项文本
                list_text = self.current_typing_text[self.typing_position + 2:end_pos]
                # 插入列表项文本
                self.chat_display.insert(tk.END, "• " + list_text, "ai_list")
                # 跳过整个列表项
                self.typing_position = end_pos
                self.chat_display.see(tk.END)
                delay = 30
                self.root.after(delay, self.type_next_character)
                return
        
        # 普通字符
        self.chat_display.insert(tk.END, char, "ai_body")
        
        self.typing_position += 1
        
        # 滚动到底部
        self.chat_display.see(tk.END)
        
        # 设置下一个字符的延迟
        delay = 50 if char in ['。', '！', '？', '，', '；', '：'] else 30
        self.root.after(delay, self.type_next_character)
    
    def start_thinking(self):
        """开始思考中状态"""
        if self.thinking_active:
            return
            
        self.thinking_active = True
        self.thinking_dots = 0
        
        # 添加思考中消息
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, "🤖 长征AI", "ai_sender")
        self.chat_display.insert(tk.END, " 正在思考中", "ai_thinking")
        
        # 记录消息ID用于后续删除
        self.thinking_message_id = self.chat_display.index(tk.END + "-2c")
        
        # 滚动到底部
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')
        
        # 开始动画
        self.animate_thinking()
    
    def animate_thinking(self):
        """思考中动画"""
        if not self.thinking_active:
            return
            
        # 更新思考中的点和图标
        self.thinking_dots = (self.thinking_dots + 1) % 4
        self.thinking_icon_index = (self.thinking_icon_index + 1) % len(self.thinking_icons)
        
        dots = "." * self.thinking_dots
        icon = self.thinking_icons[self.thinking_icon_index]
        
        # 更新显示
        self.chat_display.config(state='normal')
        
        # 删除旧的思考中文本
        if self.thinking_message_id:
            end_pos = self.chat_display.index(tk.END + "-1c")
            self.chat_display.delete(self.thinking_message_id, end_pos)
        
        # 插入新的思考中文本，使用更美观的格式
        thinking_text = f" {icon} 正在思考中{dots}"
        self.chat_display.insert(tk.END, thinking_text, "ai_thinking")
        self.thinking_message_id = self.chat_display.index(tk.END + "-1c")
        
        # 滚动到底部
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')
        
        # 继续动画，调整速度
        self.root.after(400, self.animate_thinking)
    
    def stop_thinking(self):
        """停止思考中状态"""
        if not self.thinking_active:
            return
            
        self.thinking_active = False
        
        # 删除思考中消息
        if self.thinking_message_id:
            self.chat_display.config(state='normal')
            end_pos = self.chat_display.index(tk.END + "-1c")
            self.chat_display.delete(self.thinking_message_id, end_pos)
            self.chat_display.config(state='disabled')
            self.thinking_message_id = None
        
    def clear_chat(self):
        """清空聊天记录"""
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state='disabled')
        self.status_text.config(text="长征对话记录已清空")
        
    def add_tech_decorations(self, parent):
        """添加科技感装饰元素"""
        # 添加边框装饰
        border_frame = tk.Frame(parent, bg=self.colors['accent_red'], height=2)
        border_frame.pack(fill='x', pady=(0, 10))
        
        # 添加状态指示器动画
        self.animate_status_indicator()
        
    def animate_status_indicator(self):
        """状态指示器动画"""
        if hasattr(self, 'status_indicator'):
            current_color = self.status_indicator.cget('fg')
            if current_color == self.colors['success']:
                # 连接成功时的呼吸效果
                self.status_indicator.config(fg=self.colors['accent_red_light'])
                self.root.after(500, lambda: self.status_indicator.config(fg=self.colors['success']))
            elif current_color == self.colors['error']:
                # 连接失败时的闪烁效果
                self.status_indicator.config(fg=self.colors['bg_primary'])
                self.root.after(200, lambda: self.status_indicator.config(fg=self.colors['error']))
            
            # 继续动画
            self.root.after(1000, self.animate_status_indicator)
            
    def on_input_focus_in(self, event):
        """输入框获得焦点时的处理"""
        if self.input_entry.get() == self.input_placeholder:
            self.input_entry.delete(0, tk.END)
            self.input_entry.config(foreground=self.colors['text_primary'])
            
    def on_input_focus_out(self, event):
        """输入框失去焦点时的处理"""
        if not self.input_entry.get().strip():
            self.input_entry.insert(0, self.input_placeholder)
            self.input_entry.config(foreground=self.colors['text_muted'])
            
    def on_input_click(self, event):
        """输入框点击时的处理"""
        if self.input_entry.get() == self.input_placeholder:
            self.input_entry.delete(0, tk.END)
            self.input_entry.config(foreground=self.colors['text_primary'])
            
    def on_input_key_press(self, event):
        """输入框按键时的处理"""
        if self.input_entry.get() == self.input_placeholder:
            self.input_entry.delete(0, tk.END)
            self.input_entry.config(foreground=self.colors['text_primary'])
            
    def on_input_change(self, event):
        """输入框内容变化时的处理"""
        current_text = self.input_entry.get()
        if current_text == self.input_placeholder:
            self.input_entry.config(foreground=self.colors['text_primary'])
        
    def run(self):
        """运行应用"""
        # 自动测试连接
        self.test_connection()
        
        # 启动主循环
        self.root.mainloop()

def main():
    """主函数"""
    try:
        app = AIClient()
        app.run()
    except Exception as e:
        print(f"启动客户端失败: {e}")
        messagebox.showerror("错误", f"启动失败: {e}")

if __name__ == "__main__":
    main()
