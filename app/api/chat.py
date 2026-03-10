import os
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatRequest

# 注意：这里改成了 AsyncOpenAI，防止阻塞 FastAPI
from openai import AsyncOpenAI

# 初始化异步客户端
client = AsyncOpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com"
)

router = APIRouter()


@router.post("/chat")
async def chat_with_notice(request: ChatRequest):
    # 1. 组装发给大模型的消息列表
    llm_messages = [msg.model_dump() for msg in request.history]
    llm_messages.append({"role": "user", "content": request.user_query})

    # 2. 调用大模型 API (注意这里加了 await)
    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=llm_messages,
        stream=request.stream,  # 直接把请求体里的布尔值传给 SDK
    )

    # 3. 分支处理：流式输出
    if request.stream:
        # 定义一个异步生成器
        async def generate_stream():
            # 当 stream=True 时，response 是一个异步生成器
            async for chunk in response:
                content = chunk.choices[0].delta.content
                if content is not None:
                    yield f"data: {content}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate_stream(), media_type="text/event-stream")

    else:
        full_reply = response.choices[0].message.content
        return {"status": "success", "reply": full_reply}
