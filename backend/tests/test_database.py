"""
数据库模型单元测试
"""

import pytest
from datetime import datetime

from app.database import Stock, Industry, IndicatorHistory, SignalAlert


class TestStockModel:
    """测试股票模型"""

    def test_stock_creation(self, db_session):
        """测试创建股票记录"""
        stock = Stock(code="600489", name="中金黄金", industry="贵金属")
        db_session.add(stock)
        db_session.commit()

        # 验证记录已创建
        result = db_session.query(Stock).filter_by(code="600489").first()
        assert result is not None
        assert result.code == "600489"
        assert result.name == "中金黄金"
        assert result.industry == "贵金属"
        assert result.created_at is not None

    def test_stock_unique_constraint(self, db_session):
        """测试股票代码唯一性约束"""
        # 创建第一条记录
        stock1 = Stock(code="000001", name="平安银行", industry="银行")
        db_session.add(stock1)
        db_session.commit()

        # 尝试创建相同代码的记录应该失败
        stock2 = Stock(code="000001", name="另一个银行", industry="银行")
        db_session.add(stock2)

        with pytest.raises(Exception):
            db_session.commit()

    def test_stock_without_industry(self, db_session):
        """测试创建没有行业的股票"""
        stock = Stock(code="000002", name="万科A")
        db_session.add(stock)
        db_session.commit()

        result = db_session.query(Stock).filter_by(code="000002").first()
        assert result.industry is None


class TestIndustryModel:
    """测试行业模型"""

    def test_industry_creation(self, db_session):
        """测试创建行业记录"""
        industry = Industry(name="银行", code="BK0475", stock_count=42)
        db_session.add(industry)
        db_session.commit()

        result = db_session.query(Industry).filter_by(name="银行").first()
        assert result is not None
        assert result.name == "银行"
        assert result.code == "BK0475"
        assert result.stock_count == 42

    def test_industry_unique_constraint(self, db_session):
        """测试行业名称唯一性约束"""
        industry1 = Industry(name="证券", stock_count=50)
        db_session.add(industry1)
        db_session.commit()

        industry2 = Industry(name="证券", stock_count=60)
        db_session.add(industry2)

        with pytest.raises(Exception):
            db_session.commit()


class TestIndicatorHistoryModel:
    """测试指标历史记录模型"""

    def test_indicator_history_creation(self, db_session):
        """测试创建指标历史记录"""
        history = IndicatorHistory(
            stock_code="600489",
            macd_signal="BUY",
            kdj_signal="NEUTRAL",
            rsi_value=65.5,
            rsi_signal="BUY",
            ma_signal="BUY",
            volume_signal="SELL",
            boll_signal="NEUTRAL",
            buy_signals=3,
            sell_signals=1,
            final_signal="BUY",
        )
        db_session.add(history)
        db_session.commit()

        result = (
            db_session.query(IndicatorHistory).filter_by(stock_code="600489").first()
        )
        assert result is not None
        assert result.macd_signal == "BUY"
        assert result.rsi_value == 65.5
        assert result.buy_signals == 3
        assert result.final_signal == "BUY"

    def test_indicator_history_default_values(self, db_session):
        """测试指标历史记录的默认值"""
        history = IndicatorHistory(stock_code="000001")
        db_session.add(history)
        db_session.commit()

        result = (
            db_session.query(IndicatorHistory).filter_by(stock_code="000001").first()
        )
        assert result.buy_signals == 0
        assert result.sell_signals == 0


class TestSignalAlertModel:
    """测试信号提醒模型"""

    def test_signal_alert_creation(self, db_session):
        """测试创建信号提醒"""
        alert = SignalAlert(
            stock_code="600489",
            signal_type="BUY",
            signal_count=3,
            details="MACD金叉，RSI超买",
            price=12.58,
        )
        db_session.add(alert)
        db_session.commit()

        result = db_session.query(SignalAlert).filter_by(stock_code="600489").first()
        assert result is not None
        assert result.signal_type == "BUY"
        assert result.signal_count == 3
        assert result.price == 12.58
        assert result.timestamp is not None
