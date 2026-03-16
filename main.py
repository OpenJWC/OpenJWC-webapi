from fastapi import FastAPI, Request
from app.api.v1.client import chat, notices, unbind, device
from app.api.v1.admin import auth, sysinfo, stats
from app.services.sql_db_service import SQLCLI
from app.utils.logging_manager import setup_logger
import os

ROOT_DIR = os.getcwd()
DATA_DIR = os.path.join(ROOT_DIR, "data")
BIN_DIR = os.path.join(ROOT_DIR, "bin")

app = FastAPI(title="教务处通知助手")
logger = setup_logger("main_logs")


@app.middleware("http")
async def capture_raw_request_middleware(request: Request, call_next):
    body_bytes = await request.body()

    async def receive():
        return {"type": "http.request", "body": body_bytes}

    request._receive = receive  # 覆盖底层的 receive 方法

    try:
        # 1. 拼接请求行 (例如: POST /api/login HTTP/1.1)
        raw_http = f"\n{'=' * 50}\n"
        raw_http += f"{request.method} {request.url.path}{'?' + request.url.query if request.url.query else ''} HTTP/1.1\n"

        # 2. 拼接 Headers
        for name, value in request.headers.items():
            # .title() 是为了让首字母大写，例如把 user-agent 变成 User-Agent
            raw_http += f"{name.title()}: {value}\n"

        # 3. 拼接空行和 Body
        raw_http += "\n"  # Header 和 Body 之间必须有一个空行
        if body_bytes:
            # 尝试使用 utf-8 解码，如果传的是二进制文件(如图片)，则忽略错误避免崩溃
            raw_http += body_bytes.decode("utf-8", errors="replace")

        raw_http += f"\n{'=' * 50}"

        # 打印出来
        logger.info(raw_http)

    except Exception as e:
        logger.error(f"解析请求日志时出错: {e}")

    response = await call_next(request)

    return response


# 注册各个模块的路由
app.include_router(chat.router, prefix="/api/v1/client", tags=["AI聊天"])
app.include_router(notices.router, prefix="/api/v1/client", tags=["资讯管理"])
app.include_router(unbind.router, prefix="/api/v1/client/device", tags=["客户端解绑"])
app.include_router(auth.router, prefix="/api/v1/admin/auth", tags=["管理员登录"])
app.include_router(
    sysinfo.router, prefix="/api/v1/admin/monitor", tags=["系统基本信息"]
)
app.include_router(stats.router, prefix="/api/v1/admin/monitor", tags=["基本业务信息"])
app.include_router(device.router, prefix="/api/v1/client", tags=["设备绑定信息"])


@app.get("/")
def root():
    return {"message": "Server is running!"}


if __name__ == "__main__":
    SQLCLI().cmdloop()
