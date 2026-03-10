from typing import List
from pydantic import BaseModel


class Message(BaseModel):
    role: str  # 比如 "user" 或 "assistant"
    content: str  # 具体的对话内容


# 定义请求格式的结构 (Schema)
class ChatRequest(BaseModel):
    notice_id: str
    user_query: str
    stream: bool = False
    history: List[Message] = []
