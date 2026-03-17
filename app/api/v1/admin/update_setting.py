from typing import Any, Dict
from fastapi import APIRouter, Depends
from app.core.config import ALLOWED_KEYS
from app.models.schemas import ResponseModel
from app.services.sql_db_service import db
from app.utils.logging_manager import setup_logger
from app.api.dependencies import verify_admin_token
from app.api.logging_route import LoggingRoute

logger = setup_logger("update_setting_logs")

router = APIRouter(route_class=LoggingRoute)


@router.put("/settings", response_model=ResponseModel)
async def toggle_apikey(
    settings: Dict[str, Any],
    admin_info: dict = Depends(verify_admin_token),
):
    """
    创建新的apikey。
    """
    logger.info(f"Request ID: {admin_info['x_request_id']}")
    logger.info(f"Client Version: {admin_info['x_client_version']}")
    sanitized_data = {k: v for k, v in settings.items() if k in ALLOWED_KEYS}
    if len(sanitized_data) == 0:
        return ResponseModel(msg="无匹配设置", data={})
    for key, value in sanitized_data.items():
        db.update_system_setting(key, value)
    return ResponseModel(msg="修改成功", data={})
