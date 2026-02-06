# 指标查询路由
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.monitor_service import monitor_service
from app.services.data_service import data_service

router = APIRouter(prefix="/api/indicators", tags=["indicators"])

class StockSwitchRequest(BaseModel):
    code: str
    name: str = ""

@router.get("/current")
def get_current_indicators():
    """获取当前指标"""
    result = monitor_service.check_signals()
    if result is None:
        raise HTTPException(status_code=500, detail="获取指标失败")
    return result

@router.get("/alerts")
def get_recent_alerts(limit: int = 20):
    """获取最近信号"""
    return monitor_service.get_recent_alerts(limit)

@router.post("/switch")
def switch_stock(request: StockSwitchRequest):
    """切换监控股票"""
    monitor_service.set_stock(request.code, request.name)
    return {"message": "切换成功", "code": request.code, "name": request.name}

@router.get("/quote")
def get_realtime_quote(code: str = None):
    """获取实时行情"""
    if code is None:
        code = monitor_service.current_stock
    
    quote = data_service.get_realtime_quote(code)
    if quote is None:
        raise HTTPException(status_code=500, detail="获取行情失败")
    return quote
