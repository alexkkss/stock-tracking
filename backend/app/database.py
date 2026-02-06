# 数据库模型
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True)
    name = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)

class IndicatorHistory(Base):
    __tablename__ = "indicator_history"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), index=True)
    timestamp = Column(DateTime, default=datetime.now)
    
    # 指标状态
    macd_signal = Column(String(20))
    kdj_signal = Column(String(20))
    rsi_value = Column(Float)
    rsi_signal = Column(String(20))
    ma_signal = Column(String(20))
    volume_signal = Column(String(20))
    boll_signal = Column(String(20))
    
    # 信号统计
    buy_signals = Column(Integer, default=0)
    sell_signals = Column(Integer, default=0)
    
    # 最终信号
    final_signal = Column(String(20))

class SignalAlert(Base):
    __tablename__ = "signal_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), index=True)
    timestamp = Column(DateTime, default=datetime.now)
    signal_type = Column(String(10))
    signal_count = Column(Integer)
    details = Column(Text)
    price = Column(Float)

# 数据库配置
DATABASE_URL = "sqlite:///./stock_monitor.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
