# 行业板块路由
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.industry_service import industry_service

router = APIRouter(prefix="/api/industries", tags=["行业板块"])


class IndustryResponse(BaseModel):
    """行业列表响应"""

    industries: list
    count: int


class IndustryStocksResponse(BaseModel):
    """行业股票响应"""

    industry: str
    sort_by: str
    top_gainers: list
    top_losers: list
    total_count: int
    update_time: str


class StockIndustryResponse(BaseModel):
    """股票所属行业响应"""

    code: str
    industry: Optional[str]


@router.get("/", response_model=IndustryResponse)
async def get_all_industries():
    """
    获取所有行业板块列表

    Returns:
        {
            "industries": ["银行", "证券", "保险", ...],
            "count": 86
        }
    """
    try:
        industries = industry_service.get_all_industries()
        return {"industries": industries, "count": len(industries)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取行业列表失败: {str(e)}")


@router.get("/{industry}/stocks", response_model=IndustryStocksResponse)
async def get_industry_stocks(
    industry: str,
    sort_by: str = Query(
        "change", description="排序字段: change-涨跌幅, volume-成交量, amount-成交额"
    ),
):
    """
    获取行业内的股票行情，返回前10涨幅和后10涨幅的股票

    Args:
        industry: 行业名称（如"银行"、"证券"）
        sort_by: 排序字段

    Returns:
        {
            "industry": "银行",
            "sort_by": "change",
            "top_gainers": [...],  # 前10涨幅
            "top_losers": [...],   # 后10涨幅
            "total_count": 42,
            "update_time": "2025-01-06T10:30:00"
        }
    """
    try:
        # 验证排序字段
        valid_sort_fields = ["change", "volume", "amount"]
        if sort_by not in valid_sort_fields:
            sort_by = "change"

        result = industry_service.get_industry_stocks_with_quote(industry, sort_by)

        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取行业股票失败: {str(e)}")


@router.get("/stock/{code}", response_model=StockIndustryResponse)
async def get_stock_industry(code: str):
    """
    获取指定股票所属的行业

    Args:
        code: 股票代码（如"600489"）

    Returns:
        {
            "code": "600489",
            "industry": "贵金属"
        }
    """
    try:
        industry = industry_service.get_stock_industry(code)
        return {"code": code, "industry": industry}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取股票行业失败: {str(e)}")
