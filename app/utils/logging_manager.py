import logging
from logging.handlers import RotatingFileHandler
from app.core.config import LOGS_DIR
from rich.logging import RichHandler


def setup_logger(logger_name: str) -> logging.Logger:
    """
    日志配置工厂函数。

    :param logger_name: 日志器名称。将作为日志前缀以及 logs 目录下的子文件夹名称。
    :return: 配置好的标准 logging.Logger 实例
    """
    logger = logging.getLogger(logger_name)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    console_handler = RichHandler(
        level=logging.INFO,
        rich_tracebacks=True,  # 开启 rich 的 traceback 框图
        tracebacks_show_locals=True,  # 异常时显示局部变量的值（调试神器）
        show_time=True,  # 显示时间
        show_level=True,  # 显示级别 (levelname)
        show_path=True,  # 显示调用路径和行号
        markup=True,  # 允许在日志中使用 rich 的 [color] 标签
    )
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    # 创建以 logger_name 命名的专属日志文件夹
    specific_log_dir = LOGS_DIR / logger_name
    specific_log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = specific_log_dir / f"{logger_name}.log"
    file_handler = RotatingFileHandler(
        filename=log_file_path,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,  # 保留 5 个备份文件
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)-8s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
