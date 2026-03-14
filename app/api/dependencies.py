from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.sql_db_service import db
from app.utils.logging_manager import setup_logger

logger = setup_logger("auth_logs")

# HTTPBearer 是 FastAPI 内置的工具，专门用来解析请求头里的 Authorization: Bearer <token>
security = HTTPBearer()


async def verify_api_key(
    # 自动提取 Authorization Header 中的 Token
    credentials: HTTPAuthorizationCredentials = Depends(security),
    # 强制要求请求头中必须带上 X-Device-ID
    x_device_id: str = Header(..., description="移动端设备的唯一标识 UUID"),
) -> str:
    """
    核心鉴权依赖：
    如果通过，返回提取到的 token 字符串；
    如果失败，直接在这里抛出 HTTP 异常，请求会被立刻拦截。
    """
    token = credentials.credentials
    is_valid, error_msg = db.validate_and_use_key(token, x_device_id)

    if not is_valid:
        logger.warning(
            f"鉴权拦截 - Token: {token[:8]}... 设备: {x_device_id} 原因: {error_msg}"
        )
        # 抛出 401 或 403 错误，前端会收到这个状态码
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_msg,
        )

    logger.debug(f"鉴权通过 - Token: {token[:8]}... 设备: {x_device_id}")
    return token
