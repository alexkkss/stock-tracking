# 回测服务
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.services.data_service import data_service
from app.services.indicator_service import indicator_service


class BacktestService:
    def __init__(self):
        self.data_service = data_service
        self.indicator_service = indicator_service

    def run_backtest(
        self,
        stock_code: str,
        indicators: List[str],
        hold_days: int = 5,
        days_history: int = 365,
        min_buy_signals: int = None,
    ) -> dict:
        """
        运行回测

        参数:
        - stock_code: 股票代码
        - indicators: 选择的指标列表 ['macd', 'kdj', 'rsi', 'ma', 'volume', 'boll']
        - hold_days: 持有天数
        - days_history: 回测历史天数
        - min_buy_signals: 最少买入信号数（默认等于indicators长度，即全部满足）

        返回:
        - 回测统计结果
        """
        if min_buy_signals is None:
            min_buy_signals = len(indicators)

        # 获取历史数据
        df = self.data_service.get_stock_data(stock_code, days=days_history + 50)
        if df is None or len(df) < 50:
            return {"error": "无法获取足够的历史数据"}

        trades = []

        # 从第30天开始（确保指标计算有足够数据）
        for i in range(30, len(df) - hold_days):
            # 获取当前日期的数据切片
            current_df = df.iloc[: i + 1].copy()

            # 计算指标
            indicators_result = self.indicator_service.calculate_all_indicators(
                current_df
            )
            if indicators_result is None:
                continue

            # 检查是否满足买入条件
            buy_signals = self._count_buy_signals(indicators_result, indicators)

            if buy_signals >= min_buy_signals:
                # 记录买入点
                buy_date = current_df["date"].iloc[-1]
                buy_price = current_df["close"].iloc[-1]

                # 计算卖出点（持有hold_days天后）
                if i + hold_days < len(df):
                    sell_date = df["date"].iloc[i + hold_days]
                    sell_price = df["close"].iloc[i + hold_days]

                    # 计算收益率
                    return_pct = (sell_price - buy_price) / buy_price * 100

                    trades.append(
                        {
                            "buy_date": buy_date.strftime("%Y-%m-%d")
                            if isinstance(buy_date, pd.Timestamp)
                            else str(buy_date),
                            "sell_date": sell_date.strftime("%Y-%m-%d")
                            if isinstance(sell_date, pd.Timestamp)
                            else str(sell_date),
                            "buy_price": round(float(buy_price), 2),
                            "sell_price": round(float(sell_price), 2),
                            "return_pct": round(float(return_pct), 2),
                            "signals": buy_signals,
                        }
                    )

        # 统计结果
        if not trades:
            return {
                "stock_code": stock_code,
                "total_signals": 0,
                "win_count": 0,
                "loss_count": 0,
                "win_rate": 0,
                "avg_return": 0,
                "max_return": 0,
                "min_return": 0,
                "trades": [],
            }

        returns = [t["return_pct"] for t in trades]
        win_count = sum(1 for r in returns if r > 0)
        loss_count = len(returns) - win_count

        return {
            "stock_code": stock_code,
            "indicators": indicators,
            "hold_days": hold_days,
            "days_history": days_history,
            "min_buy_signals": min_buy_signals,
            "total_signals": len(trades),
            "win_count": win_count,
            "loss_count": loss_count,
            "win_rate": round(win_count / len(trades) * 100, 2),
            "avg_return": round(np.mean(returns), 2),
            "max_return": round(max(returns), 2),
            "min_return": round(min(returns), 2),
            "trades": trades,
        }

    def _count_buy_signals(
        self, indicators_result: dict, selected_indicators: List[str]
    ) -> int:
        """计算买入信号数量"""
        count = 0

        if "macd" in selected_indicators:
            if indicators_result.get("macd", {}).get("signal") == "金叉":
                count += 1

        if "kdj" in selected_indicators:
            if indicators_result.get("kdj", {}).get("signal") == "金叉":
                count += 1

        if "rsi" in selected_indicators:
            if indicators_result.get("rsi", {}).get("signal") == "超卖":
                count += 1

        if "ma" in selected_indicators:
            if indicators_result.get("ma", {}).get("signal") == "金叉":
                count += 1

        if "volume" in selected_indicators:
            if indicators_result.get("volume", {}).get("signal") == "放量":
                count += 1

        if "boll" in selected_indicators:
            if indicators_result.get("boll", {}).get("signal") == "下轨反弹":
                count += 1

        return count

    def get_available_indicators(self) -> List[dict]:
        """获取可用的指标列表"""
        return [
            {"key": "macd", "name": "MACD金叉", "description": "MACD指标出现金叉信号"},
            {"key": "kdj", "name": "KDJ金叉", "description": "KDJ指标出现金叉信号"},
            {"key": "rsi", "name": "RSI超卖", "description": "RSI指标低于30，超卖状态"},
            {"key": "ma", "name": "均线金叉", "description": "5日均线金叉20日均线"},
            {
                "key": "volume",
                "name": "成交量放量",
                "description": "成交量大于5日均量1.5倍",
            },
            {
                "key": "boll",
                "name": "布林带下轨反弹",
                "description": "股价触及布林带下轨后反弹",
            },
        ]


backtest_service = BacktestService()
