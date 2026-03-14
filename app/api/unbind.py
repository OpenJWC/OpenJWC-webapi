from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import UnbindRequest
from app.utils.logging_manager import setup_logger
from app.api.dependencies import verify_api_key
from app.services.sql_db_service import db

logger = setup_logger("unbind_api_logs")

router = APIRouter()


@router.post("/client/device/unbind")
async def chat_with_notice(
    request: UnbindRequest, valid_token: str = Depends(verify_api_key)
):
    success = db.unbind_device(request.key_string, request.device_id)
    if not success:
        raise HTTPException(status_code=404, detail="绑定关系不存在或Key无效")
    return {"message": "解绑成功，名额已释放。"}
