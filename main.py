from fastapi import FastAPI
from app.api.v1.api_router import client_router, admin_router
from app.utils.openjwc_cli import SQLCLI
from app.utils.logging_manager import setup_logger
from contextlib import asynccontextmanager
from app.utils.ping_check import diagnose_network_environment
from app.services.sql_db_service import db
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("正在启动服务...")
    admin_user = os.getenv("INIT_ADMIN_USER")
    admin_pass = os.getenv("INIT_ADMIN_PASS")
    if admin_user and admin_pass:
        if not db.get_admin_user(admin_user):
            logger.info("未初始化管理员账号，尝试读取环境变量进行初始化..")
            db.create_admin(admin_user, admin_pass)
    api_targets = ["https://api.deepseek.com", "https://open.bigmodel.cn"]
    is_network_healthy = await diagnose_network_environment(api_targets)
    if not is_network_healthy:
        logger.error("启动警告：关键依赖网络不通，后续 API 调用可能会失败")
    yield
    logger.info("服务正在关闭...")


ROOT_DIR = os.getcwd()
DATA_DIR = os.path.join(ROOT_DIR, "data")
BIN_DIR = os.path.join(ROOT_DIR, "bin")

app = FastAPI(title="教务处通知助手", lifespan=lifespan)
logger = setup_logger("main_logs")

app.include_router(client_router, prefix="/api/v1", tags=["客户端"])
app.include_router(admin_router, prefix="/api/v1", tags=["管理员", "控制面板"])


@app.get("/")
def root():
    return {"message": "Server is running!"}


if __name__ == "__main__":
    SQLCLI().cmdloop()
