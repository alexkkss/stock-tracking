"""
行业服务单元测试
"""

import pytest
from datetime import datetime


class TestIndustryService:
    """测试行业服务类"""

    def test_get_stock_industry_existing(self, industry_service):
        """测试获取存在的股票行业"""
        # 测试已知的股票代码
        result = industry_service.get_stock_industry("600489")
        assert result == "贵金属"

    def test_get_stock_industry_not_existing(self, industry_service):
        """测试获取不存在的股票行业"""
        # 测试未知的股票代码
        result = industry_service.get_stock_industry("999999")
        assert result is None

    def test_get_all_industries(self, industry_service):
        """测试获取所有行业列表"""
        industries = industry_service.get_all_industries()

        # 验证返回的是列表
        assert isinstance(industries, list)
        # 验证包含预期的行业
        assert "贵金属" in industries
        assert "银行" in industries
        # 验证列表已排序
        assert industries == sorted(industries)

    def test_get_industry_stocks(self, industry_service):
        """测试获取行业内的股票"""
        stocks = industry_service.get_industry_stocks("银行")

        # 验证返回的是列表
        assert isinstance(stocks, list)
        # 验证包含预期股票
        assert "000001" in stocks

    def test_get_industry_stocks_not_existing(self, industry_service):
        """测试获取不存在的行业股票"""
        stocks = industry_service.get_industry_stocks("不存在的行业")
        assert stocks == []

    def test_industry_map_structure(self, industry_service):
        """测试行业映射数据结构"""
        # 验证映射表不为空
        assert len(industry_service._industry_map) > 0

        # 验证每个映射的格式
        for code, industry in industry_service._industry_map.items():
            assert isinstance(code, str)
            assert isinstance(industry, str)
            assert len(code) == 6  # A股代码为6位
            assert len(industry) > 0
