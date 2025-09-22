#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版长征大模型服务端
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import asyncio
from typing import Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="长征大模型服务", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求和响应模型
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    status: str
    timestamp: str

# 简化的AI模型
class SimpleAIModel:
    def __init__(self):
        self.conversation_history = {}
    
    async def generate_response(self, message: str, user_id: str = "default") -> str:
        """生成简单的AI响应"""
        try:
            # 模拟处理延迟
            await asyncio.sleep(0.5)
            
            # 简单的响应逻辑
            if "你好" in message or "hello" in message.lower():
                return "你好！我是长征AI，很高兴为您服务！有什么我可以帮助您的吗？"
            elif "长征" in message:
                return "长征是中国工农红军主力从长江南北各苏区向陕甘苏区的战略转移。1934年10月，中央红军开始长征，历时两年，行程二万五千里，于1936年10月胜利会师。长征是中国共产党和中国革命事业从挫折走向胜利的伟大转折点。"
            elif "再见" in message or "bye" in message.lower():
                return "再见！很高兴与您交流，期待下次再聊！"
            else:
                return f"我理解您说的是：'{message}'。这是一个很有趣的话题！作为长征AI，我很乐意与您深入讨论这个话题。请告诉我更多细节，我会尽力帮助您。"
            
        except Exception as e:
            logger.error(f"生成响应时出错: {e}")
            return "抱歉，我现在无法处理您的请求，请稍后再试。"
    
    def get_conversation_history(self, user_id: str) -> list:
        """获取对话历史"""
        return self.conversation_history.get(user_id, [])
    
    def add_to_history(self, user_id: str, user_message: str, ai_response: str):
        """添加到对话历史"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "user": user_message,
            "ai": ai_response,
            "timestamp": asyncio.get_event_loop().time()
        })

# 初始化AI模型
ai_model = SimpleAIModel()

@app.get("/")
async def root():
    """根路径"""
    return {"message": "长征大模型服务正在运行", "status": "online"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "ai-model-server"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """聊天接口"""
    try:
        logger.info(f"收到消息: {request.message}")
        
        # 生成AI响应
        response = await ai_model.generate_response(request.message, request.user_id)
        
        # 添加到对话历史
        ai_model.add_to_history(request.user_id, request.message, response)
        
        # 返回响应
        return ChatResponse(
            response=response,
            status="success",
            timestamp=str(asyncio.get_event_loop().time())
        )
        
    except Exception as e:
        logger.error(f"处理聊天请求时出错: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

if __name__ == "__main__":
    print("🚀 启动长征大模型服务...")
    print("📍 服务地址: http://localhost:8001")
    print("📖 API文档: http://localhost:8001/docs")
    
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
