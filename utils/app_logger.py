import logging
import os
from logging.handlers import TimedRotatingFileHandler


def get_logger(logger_name="MyLogger", log_dir="./logs/", log_file="app.log"):
    """
    配置并返回一个日志对象。

    Args:
        logger_name (str): 日志记录器的名称。
        log_dir (str): 日志文件的目录。
        log_file (str): 日志文件名。

    Returns:
        logging.Logger: 配置好的日志对象。
    """
    # 确保日志目录存在
    log_dir = os.path.abspath(log_dir)
    os.makedirs(log_dir, exist_ok=True)

    # 日志文件路径
    log_path = os.path.join(log_dir, log_file)

    # 获取 logger 实例
    logger = logging.getLogger(logger_name)

    # 避免重复添加处理器
    if not logger.hasHandlers():
        # 设置日志级别
        logger.setLevel(logging.INFO)

        # 创建 TimedRotatingFileHandler
        handler = TimedRotatingFileHandler(
            filename=log_path,
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8"
        )

        # 配置日志格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # 添加处理器到 logger
        logger.addHandler(handler)

    return logger
