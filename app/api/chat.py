from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatRequest
from app.services.ai_service import client
from app.utils.logging_manager import setup_logger
import app.services.ai_service as ai_service

logger = setup_logger("chat_api_logs")

router = APIRouter()


@router.post("/chat")
async def chat_with_notice(request: ChatRequest):
    logger.info("接受到LLM聊天请求")
    response = await ai_service.get_ai_response(request, use_rag=True)
    # 3. 分支处理：流式输出
    if request.stream:
        logger.info("尝试流式输出")
        return StreamingResponse(
            ai_service.generate_stream(response), media_type="text/event-stream"
        )

    else:
        logger.info("尝试非流式输出")
        full_reply = response.choices[0].message.content
        return {"status": "success", "reply": full_reply}
