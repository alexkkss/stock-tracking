#!/bin/bash

# A股股票监控系统启动脚本

echo "=========================================="
echo "    A股股票监控系统启动器"
echo "=========================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3.9+"
    exit 1
fi

# 检查Node
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js，请先安装Node.js 18+"
    exit 1
fi

# 切换到脚本所在目录
cd "$(dirname "$0")"
BASE_DIR=$(pwd)

# 创建日志目录
mkdir -p backend/logs

# 启动后端
echo "正在启动后端服务..."
cd backend
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt

# 生成日志文件名（带时间戳）
LOG_FILE="logs/backend_$(date +%Y%m%d_%H%M%S).log"
PID_FILE="logs/backend.pid"

echo "启动后端服务 (http://localhost:8000)..."
echo "后端日志保存至: backend/$LOG_FILE"
nohup python run.py > "$LOG_FILE" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$PID_FILE"

echo "后端PID: $BACKEND_PID"
echo "查看日志: tail -f backend/$LOG_FILE"
echo ""

# 等待后端启动
sleep 3

# 检查后端是否启动成功
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "错误: 后端服务启动失败，请检查日志: backend/$LOG_FILE"
    cd "$BASE_DIR"
    exit 1
fi

cd "$BASE_DIR"

# 启动前端
echo "正在启动前端服务..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

echo "启动前端服务 (http://localhost:3000)..."
npm run dev &
FRONTEND_PID=$!
cd "$BASE_DIR"

echo "前端PID: $FRONTEND_PID"
echo ""
echo "=========================================="
echo "系统已启动！"
echo ""
echo "后端API: http://localhost:8000"
echo "前端界面: http://localhost:3000"
echo "后端日志: tail -f backend/logs/backend_*.log"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=========================================="

# 捕获退出信号
trap "echo ''; echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f backend/logs/backend.pid; exit" INT

# 保持运行
wait