# 回测路由
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from app.services.backtest_service import backtest_service

router = APIRouter(prefix="/api/backtest", tags=["backtest"])


class BacktestRequest(BaseModel):
    stock_code: str = Field(..., description="股票代码")
    indicators: List[str] = Field(..., description="选择的指标组合")
    hold_days: int = Field(default=5, ge=1, le=30, description="持有天数")
    days_history: int = Field(default=365, ge=30, le=1095, description="回测历史天数")
    min_buy_signals: int = Field(
        default=None, description="最少买入信号数（默认等于indicators长度）"
    )


class BacktestResponse(BaseModel):
    stock_code: str
    indicators: List[str]
    hold_days: int
    days_history: int
    min_buy_signals: int
    total_signals: int
    win_count: int
    loss_count: int
    win_rate: float
    avg_return: float
    max_return: float
    min_return: float
    trades: List[dict]


@router.post("/run", response_model=BacktestResponse)
def run_backtest(request: BacktestRequest):
    """运行回测"""
    # 验证指标
    available_indicators = [
        i["key"] for i in backtest_service.get_available_indicators()
    ]
    invalid_indicators = [
        i for i in request.indicators if i not in available_indicators
    ]
    if invalid_indicators:
        raise HTTPException(status_code=400, detail=f"无效的指标: {invalid_indicators}")

    # 运行回测
    result = backtest_service.run_backtest(
        stock_code=request.stock_code,
        indicators=request.indicators,
        hold_days=request.hold_days,
        days_history=request.days_history,
        min_buy_signals=request.min_buy_signals,
    )

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.get("/indicators")
def get_available_indicators():
    """获取可用的指标列表"""
    return backtest_service.get_available_indicators()


@router.get("/example")
def get_example():
    """获取回测示例"""
    return {
        "description": "回测示例：测试MACD+KDJ+RSI组合在过去1年中的表现",
        "request": {
            "stock_code": "600489",
            "indicators": ["macd", "kdj", "rsi"],
            "hold_days": 5,
            "days_history": 365,
            "min_buy_signals": 3,
        },
    }
