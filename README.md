# AI大模型C/S架构应用

一个基于Python的AI大模型客户端-服务端应用，具有科技感的红色主题UI和视频播放功能。

## 功能特性

- 🤖 **智能对话**: 基于大模型的智能对话系统
- 🎥 **视频播放**: 支持AI人形视频播放
- 🎨 **科技UI**: 红色主题的科技感界面设计
- 🌐 **C/S架构**: 客户端-服务端分离架构
- 💬 **实时聊天**: 实时消息交互
- 📱 **响应式设计**: 支持窗口大小调整

## 项目结构

```
Long_March/
├── server.py              # 服务端代码 (FastAPI)
├── client.py              # 客户端代码 (Tkinter)
├── requirements.txt       # 依赖包列表
├── start_server.bat       # 服务端启动脚本
├── start_client.bat       # 客户端启动脚本
├── start_all.bat          # 一键启动脚本
├── README.md              # 项目说明
└── resources/
    └── ai_avatar.mp4      # AI人形视频文件
```

## 安装和运行

### 环境要求

- Python 3.8+
- Windows 10/11 (推荐) 以及Linux

### 快速开始

1. **一键启动** (推荐)
   ```bash
   # 安装依赖
   pip install -r requirements.txt
   # 运行
   先运行server端，再运行client端
   ```

2. **Linux启动**
   ```bash
   # 安装依赖
   pip install -r requirements.txt
   
   # 启动服务端
   python server.py
   
   # 启动客户端 (新开一个命令行窗口)
   python client.py
   ```

## 使用说明

### 服务端
- 默认运行在 `http://localhost:8000`

### 客户端
1. **连接测试**: 点击"测试连接"按钮检查服务端连接状态
2. **视频播放**: 点击"播放"按钮开始播放AI人形视频
3. **智能对话**: 在输入框中输入问题，按回车或点击"发送"按钮
4. **清空聊天**: 点击"清空"按钮清空聊天记录

## 技术架构

### 服务端 (server.py)
- **框架**: FastAPI
- **功能**: 
  - RESTful API接口
  - 大模型对话处理
  - 对话历史管理
  - CORS跨域支持

### 客户端 (client.py)
- **框架**: Tkinter + PIL + OpenCV
- **功能**:
  - 科技感UI界面
  - 视频播放控制
  - 实时聊天交互
  - 连接状态监控

## 自定义配置

### 修改服务端端口
编辑 `server.py` 文件中的端口配置:
```python
uvicorn.run(
    "server:app",
    host="0.0.0.0",
    port=8000,  # 修改这里
    reload=True
)
```

### 修改客户端连接地址
编辑 `client.py` 文件中的服务器地址:
```python
self.server_url = "http://localhost:8000"  # 修改这里
```

### 添加新的AI响应规则
编辑 `server.py` 文件中的 `AIModel.generate_response` 方法:
```python
responses = {
    "你好": "你好！我是AI助手，很高兴为您服务！",
    # 添加新的响应规则
    "你的名字": "我叫AI助手，很高兴认识您！",
}
```

## 故障排除

### 常见问题

1. **连接失败**
   - 确保服务端已启动
   - 检查防火墙设置
   - 确认端口8000未被占用

2. **依赖安装失败**
   - 确保Python版本 >= 3.8
   - 尝试使用管理员权限运行
   - 检查网络连接

### 日志查看

- 服务端日志会在命令行窗口中显示
- 客户端错误会通过弹窗提示

## 开发说明

### 扩展功能

1. **接入真实大模型API**
   - 修改 `server.py` 中的 `AIModel.generate_response` 方法
   - 集成OpenAI、百度文心一言等API

2. **添加更多UI功能**
   - 修改 `client.py` 中的界面布局
   - 添加更多交互元素

3. **优化视频播放**
   - 支持更多视频格式
   - 添加播放控制功能

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 邮箱: [oadxh0806@126.com]

