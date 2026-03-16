from fastapi import APIRouter, Depends, Path
from app.models.schemas import ResponseModel
from app.services.sql_db_service import db
from app.utils.logging_manager import setup_logger
from app.api.dependencies import verify_admin_token
from app.api.logging_route import LoggingRoute

logger = setup_logger("delete_apikey_logs")

router = APIRouter(route_class=LoggingRoute)


@router.delete("/{key_id}", response_model=ResponseModel)
async def toggle_apikey(
    key_id: int = Path(description="目标apikey"),
    admin_info: dict = Depends(verify_admin_token),
):
    """
    删除apikey。
    """
    logger.info(f"Request ID: {admin_info['x_request_id']}")
    logger.info(f"Client Version: {admin_info['x_client_version']}")

    try:
        db.delete_api_key(key_id)
        logger.info("API key deleted successfully.")
        return ResponseModel(msg="APIkey删除成功。", data={})
    except Exception as e:
        logger.error(f"Error deleting API key: {e}")
        return ResponseModel(msg="APIkey删除失败。", data={})
