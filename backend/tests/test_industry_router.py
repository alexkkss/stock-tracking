"""
行业路由API单元测试
"""

import pytest


class TestIndustryRouter:
    """测试行业路由API"""

    def test_get_all_industries(self, test_client):
        """测试获取所有行业列表API"""
        response = test_client.get("/api/industries/")

        # 验证状态码
        assert response.status_code == 200

        # 验证响应结构
        data = response.json()
        assert "industries" in data
        assert "count" in data
        assert isinstance(data["industries"], list)
        assert isinstance(data["count"], int)

    def test_get_stock_industry(self, test_client):
        """测试获取股票所属行业API"""
        response = test_client.get("/api/industries/stock/600489")

        # 验证状态码
        assert response.status_code == 200

        # 验证响应结构
        data = response.json()
        assert "code" in data
        assert "industry" in data
        assert data["code"] == "600489"

    def test_get_stock_industry_invalid_code(self, test_client):
        """测试获取无效股票代码的行业"""
        response = test_client.get("/api/industries/stock/invalid")

        # 应该返回200，但industry为null
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "invalid"

    def test_get_industry_stocks(self, test_client):
        """测试获取行业股票列表API"""
        # 使用URL编码处理中文字符
        response = test_client.get("/api/industries/%E8%B4%B5%E9%87%91%E5%B1%9E/stocks")

        # 验证状态码
        assert response.status_code == 200

        # 验证响应结构
        data = response.json()
        assert "industry" in data
        assert "sort_by" in data
        assert "top_gainers" in data
        assert "top_losers" in data
        assert "total_count" in data
        assert "update_time" in data

        # 验证数据类型
        assert isinstance(data["top_gainers"], list)
        assert isinstance(data["top_losers"], list)
        assert isinstance(data["total_count"], int)

    def test_get_industry_stocks_with_sort_by(self, test_client):
        """测试带排序参数的行业股票API"""
        response = test_client.get(
            "/api/industries/%E8%B4%B5%E9%87%91%E5%B1%9E/stocks?sort_by=volume"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["sort_by"] == "volume"

    def test_get_industry_stocks_invalid_sort(self, test_client):
        """测试无效的排序参数"""
        response = test_client.get(
            "/api/industries/%E8%B4%B5%E9%87%91%E5%B1%9E/stocks?sort_by=invalid"
        )

        # 应该返回200，但使用默认排序
        assert response.status_code == 200
        data = response.json()
        # 验证默认使用change排序
        assert data["sort_by"] == "change"
