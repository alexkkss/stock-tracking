# 股票监控系统配置
import os
from dataclasses import dataclass

@dataclass
class Config:
    # 股票配置
    DEFAULT_STOCK_CODE = "600489"
    DEFAULT_STOCK_NAME = "中金黄金"
    
    # 监控配置
    MONITOR_INTERVAL = 60  # 秒
    SIGNAL_THRESHOLD = 4   # 触发信号的指标数量阈值
    
    # 指标参数
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    RSI_PERIOD = 14
    KDJ_PERIOD = 9
    MA_SHORT = 5
    MA_LONG = 20
    BOLL_PERIOD = 20
    BOLL_STD = 2
    
    # 数据库
    DATABASE_URL = "sqlite:///./stock_monitor.db"
    
    # API配置
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL = 30

config = Config()
