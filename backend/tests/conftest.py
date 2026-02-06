"""
Pytest配置和Fixtures
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal, Base, engine
from app.services.industry_service import IndustryService


@pytest.fixture(scope="session")
def test_client():
    """创建测试客户端"""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def db_session():
    """创建数据库会话"""
    # 创建测试数据库表
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        # 清理测试数据
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def industry_service():
    """创建行业服务实例"""
    service = IndustryService()
    # 初始化测试数据
    service._industry_map = {
        "600489": "贵金属",
        "000001": "银行",
        "000002": "房地产",
        "600519": "酿酒行业",
        "601318": "保险",
    }
    service._last_update = None
    return service
