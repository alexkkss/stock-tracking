# FastAPI主应用
import asyncio
import json
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from contextlib import asynccontextmanager

from app.database import init_db
from app.routers import stocks, indicators, backtest, industries
from app.services.monitor_service import monitor_service

# 存储WebSocket连接
websocket_connections: list = []


async def broadcast_to_clients(message: dict):
    """广播消息到所有WebSocket客户端"""
    disconnected = []
    for ws in websocket_connections:
        try:
            await ws.send_json(message)
        except Exception:
            disconnected.append(ws)

    # 移除断开的连接
    for ws in disconnected:
        if ws in websocket_connections:
            websocket_connections.remove(ws)


def on_signal_triggered(result: dict):
    """信号触发回调"""
    asyncio.create_task(broadcast_to_clients({"type": "signal", "data": result}))


async def monitor_task():
    """定时监控任务"""
    result = monitor_service.check_signals()
    if result:
        await broadcast_to_clients({"type": "indicators", "data": result})


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    init_db()
    monitor_service.register_callback(on_signal_triggered)

    # 启动调度器
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        monitor_task,
        trigger=IntervalTrigger(seconds=60),
        id="monitor_task",
        replace_existing=True,
    )
    scheduler.start()

    print("=" * 50)
    print("股票监控系统已启动")
    print(f"监控股票: {monitor_service.current_stock} {monitor_service.stock_name}")
    print("=" * 50)

    yield

    # 关闭时清理
    scheduler.shutdown()
    print("股票监控系统已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="股票监控系统",
    description="A股技术指标监控与信号提醒系统",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(stocks.router)
app.include_router(indicators.router)
app.include_router(backtest.router)
app.include_router(industries.router)


# WebSocket端点
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_connections.append(websocket)
    print(f"WebSocket客户端已连接，当前连接数: {len(websocket_connections)}")

    try:
        while True:
            # 接收心跳
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "ping":
                await websocket.send_json(
                    {"type": "pong", "time": datetime.now().isoformat()}
                )

    except WebSocketDisconnect:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)
        print(f"WebSocket客户端已断开，当前连接数: {len(websocket_connections)}")
    except Exception as e:
        print(f"WebSocket错误: {e}")
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)


@app.get("/")
def root():
    return {
        "message": "股票监控系统API",
        "status": "running",
        "current_stock": monitor_service.current_stock,
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
