from fastapi import APIRouter, Depends
from app.models.schemas import ResponseModel
from app.services.sql_db_service import db
from app.api.dependencies import verify_api_key
from app.utils.logging_manager import setup_logger
from app.api.logging_route import LoggingRoute

logger = setup_logger("get_labels_logs")

router = APIRouter(route_class=LoggingRoute)


# TODO: 获取所有标签的接口。
@router.get("/labels", response_model=ResponseModel)
async def get_latest_notices(
    valid_token: str = Depends(verify_api_key),
):
    """
    获取所有标签。
    """
    return ResponseModel(msg="获取成功", data={"labels": db.get_labels()})
