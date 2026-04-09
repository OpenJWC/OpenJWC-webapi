from fastapi import APIRouter, Depends
from app.models.schemas import (
    ResponseModel,
    SemanticSearchRequest,
)
from app.services.sql_db_service import db
from app.services.vector_db_service import vector_db
from app.utils.logging_manager import setup_logger
from app.api.logging_route import LoggingRoute
from app.api.dependencies import verify_api_key
from asyncio import to_thread

logger = setup_logger("search_logs")

router = APIRouter(prefix="/notices/search", route_class=LoggingRoute)


@router.post("", response_model=ResponseModel)
async def semantic_search(
    request: SemanticSearchRequest,
    valid_token: str = Depends(verify_api_key),
):
    """
    语义搜索资讯接口（强制鉴权，消耗嵌入模型额度）

    Args:
        request: 搜索请求，包含查询文本、返回数量上限、最低相似度阈值

    Returns:
        带相似度分数和元信息的搜索结果
    """
    logger.info(
        f"接受到语义搜索请求: {request.query[:50]}... Token: {valid_token[:8]}..."
    )

    # 获取系统默认相似度阈值
    min_similarity = request.min_similarity
    if min_similarity is None:
        min_similarity = float(db.get_system_setting("search_min_similarity"))

    # 限制 top_k 范围
    top_k = max(1, min(request.top_k, 20))

    # 执行语义搜索
    search_results = await to_thread(
        vector_db.search_with_metadata, request.query, top_k, min_similarity
    )

    final_results = []
    for result in search_results:
        final_results.append(result)

    logger.info(f"语义搜索完成，返回 {len(final_results)} 条结果")

    return ResponseModel(
        msg="搜索成功",
        data={
            "total_found": len(final_results),
            "results": final_results,
        },
    )
