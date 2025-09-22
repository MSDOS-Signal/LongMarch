#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI大模型服务端
基于FastAPI构建的C/S架构服务端
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import sys
import json
import asyncio
from typing import Optional
import logging
import httpx

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SiliconFlow API配置
SILICONFLOW_API_KEY = "sk-jisussvbdngycoyhktajjvfqakobrrunazkucdbkjjrxyoyh"
SILICONFLOW_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
MODEL_NAME = "THUDM/GLM-4-9B-0414"

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

# 智能AI模型（使用SiliconFlow API）
class AIModel:
    def __init__(self):
        self.conversation_history = {}
        self.api_key = SILICONFLOW_API_KEY
        self.api_url = SILICONFLOW_API_URL
        self.model_name = MODEL_NAME
    
    async def generate_response(self, message: str, user_id: str = "default") -> str:
        """使用SiliconFlow API生成智能AI响应"""
        try:
            # 获取对话历史
            history = self.conversation_history.get(user_id, [])
            
            # 构建消息列表
            messages = self._build_messages(message, history)
            
            # 调用SiliconFlow API
            response = await self._call_siliconflow_api(messages)
            
            return response
            
        except Exception as e:
            logger.error(f"生成响应时出错: {e}")
            return "抱歉，我现在无法处理您的请求，请稍后再试。"
    
    def _build_messages(self, user_message: str, history: list) -> list:
        """构建消息列表"""
        messages = [
            {
                "role": "system",
                "content": "你是长征AI，一个智能助手。你具有丰富的知识，能够回答各种问题，进行深入对话，并提供有价值的建议。请用友好、专业、有根据的方式与用户交流。"
            }
        ]
        
        # 添加历史对话（最近5轮）
        recent_history = history[-5:] if len(history) > 5 else history
        for exchange in recent_history:
            messages.append({
                "role": "user",
                "content": exchange.get("user", "")
            })
            messages.append({
                "role": "assistant", 
                "content": exchange.get("ai", "")
            })
        
        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    async def _call_siliconflow_api(self, messages: list) -> str:
        """调用SiliconFlow API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": 2048,
            "temperature": 0.7,
            "top_p": 0.9,
            "stream": False
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        return data["choices"][0]["message"]["content"]
                    else:
                        logger.error(f"API响应格式异常: {data}")
                        return "抱歉，我无法生成合适的响应。"
                else:
                    logger.error(f"API调用失败: {response.status_code}, {response.text}")
                    return "抱歉，服务暂时不可用，请稍后再试。"
                    
        except httpx.TimeoutException:
            logger.error("API调用超时")
            return "抱歉，请求超时，请稍后再试。"
        except httpx.RequestError as e:
            logger.error(f"API请求错误: {e}")
            return "抱歉，网络连接出现问题，请检查网络后重试。"
        except Exception as e:
            logger.error(f"未知错误: {e}")
            return "抱歉，发生了未知错误，请稍后再试。"
    
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
ai_model = AIModel()

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

@app.get("/history/{user_id}")
async def get_history(user_id: str):
    """获取对话历史"""
    try:
        history = ai_model.get_conversation_history(user_id)
        return {"history": history, "status": "success"}
    except Exception as e:
        logger.error(f"获取历史记录时出错: {e}")
        raise HTTPException(status_code=500, detail="获取历史记录失败")

@app.delete("/history/{user_id}")
async def clear_history(user_id: str):
    """清空对话历史"""
    try:
        if user_id in ai_model.conversation_history:
            del ai_model.conversation_history[user_id]
        return {"message": "历史记录已清空", "status": "success"}
    except Exception as e:
        logger.error(f"清空历史记录时出错: {e}")
        raise HTTPException(status_code=500, detail="清空历史记录失败")

if __name__ == "__main__":
    print("🚀 启动长征大模型服务...")

    # 在打包后的可执行文件中关闭自动重载，并直接传递 app 对象
    is_frozen = getattr(sys, "frozen", False)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=not is_frozen,
        log_level="info"
    )
