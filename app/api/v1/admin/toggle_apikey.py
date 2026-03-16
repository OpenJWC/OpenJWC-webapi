from fastapi import APIRouter, Depends, Path
from app.models.schemas import ResponseModel, ToggleApiKeyRequest
from app.services.sql_db_service import db
from app.utils.logging_manager import setup_logger
from app.api.dependencies import verify_admin_token
from app.api.logging_route import LoggingRoute

logger = setup_logger("toggle_apikey_logs")

router = APIRouter(route_class=LoggingRoute)


@router.put("/{key_id}/status", response_model=ResponseModel)
async def toggle_apikey(
    request: ToggleApiKeyRequest,
    key_id: int = Path(description="目标apikey"),
    admin_info: dict = Depends(verify_admin_token),
):
    """
    创建新的apikey。
    """
    logger.info(f"Request ID: {admin_info['x_request_id']}")
    logger.info(f"Client Version: {admin_info['x_client_version']}")
    try:
        db.toggle_key_status(key_id=key_id, is_active=request.is_active)
        logger.info(f"{key_id}的apikey启用状态已调整为{request.is_active}")
        return ResponseModel(
            msg=f"{key_id}的启用状态调整为{request.is_active}", data={}
        )
    except Exception as e:
        logger.error(f"启停apikey时遇到未知错误: {e}")
        return ResponseModel(msg="启停apikey时遇到未知错误", data={})
