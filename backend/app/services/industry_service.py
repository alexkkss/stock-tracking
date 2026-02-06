# 行业板块服务
import akshare as ak
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd

from app.database import get_db, Stock, Industry


class IndustryService:
    """行业板块数据服务"""

    def __init__(self):
        self._industry_map: Dict[str, str] = {}  # 股票代码->行业名称映射
        self._last_update: Optional[datetime] = None

    def _refresh_industry_map(self):
        """刷新行业映射缓存"""
        try:
            # 使用akshare获取行业板块数据
            # 获取东方财富行业板块
            df = ak.stock_board_industry_name_em()

            industry_map = {}
            for _, row in df.iterrows():
                industry_name = row["板块名称"]
                try:
                    # 获取该行业下的所有股票
                    stocks_df = ak.stock_board_industry_cons_em(symbol=industry_name)
                    for _, stock_row in stocks_df.iterrows():
                        code = stock_row["代码"]
                        industry_map[code] = industry_name
                except Exception as e:
                    print(f"获取行业 {industry_name} 股票列表失败: {e}")
                    continue

            self._industry_map = industry_map
            self._last_update = datetime.now()
            print(f"行业映射刷新完成，共 {len(industry_map)} 只股票")

        except Exception as e:
            print(f"刷新行业映射失败: {e}")

    def get_stock_industry(self, code: str) -> Optional[str]:
        """获取股票所属行业"""
        # 检查缓存是否过期（超过24小时）
        if self._last_update is None or (datetime.now() - self._last_update).days >= 1:
            self._refresh_industry_map()

        return self._industry_map.get(code)

    def get_all_industries(self) -> List[str]:
        """获取所有行业列表"""
        if self._last_update is None or (datetime.now() - self._last_update).days >= 1:
            self._refresh_industry_map()

        # 返回唯一行业列表并排序
        industries = list(set(self._industry_map.values()))
        return sorted(industries)

    def get_industry_stocks(self, industry_name: str) -> List[str]:
        """获取行业内的所有股票代码"""
        if self._last_update is None or (datetime.now() - self._last_update).days >= 1:
            self._refresh_industry_map()

        # 筛选该行业下的所有股票
        stocks = [
            code
            for code, industry in self._industry_map.items()
            if industry == industry_name
        ]
        return stocks

    def get_industry_stocks_with_quote(
        self, industry_name: str, sort_by: str = "change"
    ) -> Dict:
        """
        获取行业内股票行情数据，返回前10涨幅和后10涨幅的股票

        Args:
            industry_name: 行业名称
            sort_by: 排序字段 (change-涨跌幅, volume-成交量, amount-成交额)

        Returns:
            {
                "industry": "行业名称",
                "sort_by": "排序字段",
                "top_gainers": [...],  # 前10涨幅
                "top_losers": [...],   # 后10涨幅（跌幅最大）
                "total_count": 股票总数,
                "update_time": 更新时间
            }
        """
        try:
            # 获取行业内所有股票
            stock_codes = self.get_industry_stocks(industry_name)

            if not stock_codes:
                return {
                    "industry": industry_name,
                    "sort_by": sort_by,
                    "top_gainers": [],
                    "top_losers": [],
                    "total_count": 0,
                    "update_time": datetime.now().isoformat(),
                }

            # 获取实时行情数据
            df = ak.stock_zh_a_spot_em()

            # 筛选该行业股票
            industry_df = df[df["代码"].isin(stock_codes)].copy()

            if industry_df.empty:
                return {
                    "industry": industry_name,
                    "sort_by": sort_by,
                    "top_gainers": [],
                    "top_losers": [],
                    "total_count": 0,
                    "update_time": datetime.now().isoformat(),
                }

            # 映射字段名
            field_map = {"change": "涨跌幅", "volume": "成交量", "amount": "成交额"}

            sort_field = field_map.get(sort_by, "涨跌幅")

            # 按指定字段排序
            industry_df = industry_df.sort_values(by=sort_field, ascending=False)

            # 转换为列表
            def row_to_dict(row):
                return {
                    "code": row["代码"],
                    "name": row["名称"],
                    "price": float(row["最新价"]) if pd.notna(row["最新价"]) else 0,
                    "change": float(row["涨跌幅"]) if pd.notna(row["涨跌幅"]) else 0,
                    "change_amount": float(row["涨跌额"])
                    if pd.notna(row["涨跌额"])
                    else 0,
                    "volume": float(row["成交量"]) if pd.notna(row["成交量"]) else 0,
                    "amount": float(row["成交额"]) if pd.notna(row["成交额"]) else 0,
                    "turnover": float(row["换手率"]) if pd.notna(row["换手率"]) else 0,
                    "high": float(row["最高"]) if pd.notna(row["最高"]) else 0,
                    "low": float(row["最低"]) if pd.notna(row["最低"]) else 0,
                    "open": float(row["今开"]) if pd.notna(row["今开"]) else 0,
                    "pre_close": float(row["昨收"]) if pd.notna(row["昨收"]) else 0,
                }

            # 获取前10和后10
            all_stocks = [row_to_dict(row) for _, row in industry_df.iterrows()]

            if len(all_stocks) <= 20:
                # 如果总数<=20，则分成两半
                mid = len(all_stocks) // 2
                top_gainers = all_stocks[:mid] if mid > 0 else []
                top_losers = all_stocks[mid:] if len(all_stocks) > mid else []
            else:
                top_gainers = all_stocks[:10]
                top_losers = all_stocks[-10:]

            return {
                "industry": industry_name,
                "sort_by": sort_by,
                "top_gainers": top_gainers,
                "top_losers": top_losers,
                "total_count": len(all_stocks),
                "update_time": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"获取行业 {industry_name} 股票行情失败: {e}")
            return {
                "industry": industry_name,
                "sort_by": sort_by,
                "top_gainers": [],
                "top_losers": [],
                "total_count": 0,
                "update_time": datetime.now().isoformat(),
                "error": str(e),
            }


# 创建单例
industry_service = IndustryService()
