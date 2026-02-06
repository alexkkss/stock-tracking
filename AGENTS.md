# Agent Guidelines for Stock Tracking Project

## 项目概述
A股股票监控系统 - 实时监控技术指标（MACD、KDJ、RSI、均线、成交量、布林带）

**架构**: 前端(Vue 3) + 后端(FastAPI) + SQLite数据库

## 启动命令

### 一键启动（推荐）
```bash
./start.sh          # 启动前后端服务
```

### 后端（Python）
```bash
cd backend
source venv/bin/activate  # 激活虚拟环境
pip install -r requirements.txt
python run.py             # 开发模式（带热重载）
# 服务运行在 http://localhost:8000
```

### 前端（Vue）
```bash
cd frontend
npm install               # 首次安装依赖
npm run dev               # 开发服务器
npm run build             # 生产构建
# 服务运行在 http://localhost:3000
```

## 测试命令

**注意**: 项目尚未配置测试框架。如需添加测试：
- **后端**: 使用 `pytest` (Python)
- **前端**: 使用 `vitest` 或 `jest` (Vue)

### 运行单个测试（添加后）
```bash
# Python (pytest)
pytest tests/test_indicators.py::test_macd -v

# JavaScript (vitest)
npx vitest run src/components/SignalAlert.test.js
```

## 代码风格规范

### Python（后端）

**导入顺序**: 标准库 → 第三方库 → 本地模块
```python
# 标准库
import json
from datetime import datetime

# 第三方库
from fastapi import FastAPI
from sqlalchemy import create_engine

# 本地模块
from app.database import init_db
from app.services.monitor_service import monitor_service
```

**命名规范**:
- 类名: `PascalCase` (如 `IndicatorService`)
- 函数/变量: `snake_case` (如 `calculate_macd`, `current_price`)
- 常量: `UPPER_CASE` (如 `DATABASE_URL`)
- 私有方法: `_snake_case` 前缀下划线

**类型注解**: 使用类型提示
```python
from typing import Optional, Dict, List

def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> dict:
    ...
```

**错误处理**:
```python
try:
    result = await fetch_data()
except Exception as e:
    print(f"错误信息: {e}")
    raise HTTPException(status_code=500, detail="操作失败")
```

**注释规范**: 中文注释，函数使用文档字符串
```python
def calculate_macd(self, df: pd.DataFrame) -> dict:
    """计算MACD指标
    
    Args:
        df: 包含收盘价数据的DataFrame
        
    Returns:
        包含DIF、DEA、MACD值和信号的字典
    """
```

### JavaScript/Vue（前端）

**导入顺序**: Vue核心 → 第三方库 → 本地组件/服务
```javascript
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { TrendCharts } from '@element-plus/icons-vue'

import SignalAlert from './components/SignalAlert.vue'
import { api } from './services/api'
```

**命名规范**:
- 组件名: `PascalCase` (如 `SignalAlert.vue`)
- 函数/变量: `camelCase` (如 `currentStock`, `fetchData`)
- 常量: `UPPER_CASE` (如 `API_BASE`, `WS_URL`)
- 组合式函数: 前缀 `use` (如 `useStockData`)

**Vue 3 组合式 API 规范**:
```javascript
export default {
  name: 'Dashboard',
  components: { SignalAlert },
  setup() {
    // 响应式数据
    const currentStock = reactive({ code: '', name: '' })
    const isLoading = ref(false)
    
    // 方法
    const fetchData = async () => {
      try {
        isLoading.value = true
        const data = await api.getIndicators()
        return data
      } catch (error) {
        console.error('获取数据失败:', error)
      } finally {
        isLoading.value = false
      }
    }
    
    // 生命周期
    onMounted(fetchData)
    
    return { currentStock, isLoading, fetchData }
  }
}
```

**模板规范**:
- 使用双引号
- 组件标签自闭合: `<SignalAlert />`
- 事件处理使用 `@` 语法糖
- 属性绑定使用 `:` 语法糖

```vue
<template>
  <div class="dashboard">
    <el-card>
      <SignalAlert 
        v-model:visible="alertVisible"
        :signal="latestSignal"
        @confirm="handleConfirm"
      />
    </el-card>
  </div>
</template>
```

**样式规范**:
- 使用 `scoped` 属性
- 类名使用 `kebab-case`
- 颜色使用 Element Plus 变量

```vue
<style scoped>
.dashboard {
  background: #f5f7fa;
}

.stock-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>
```

## API 端点规范

**基础路径**: `/api`

**路由文件位置**:
- 指标相关: `backend/app/routers/indicators.py`
- 股票相关: `backend/app/routers/stocks.py`
- 回测相关: `backend/app/routers/backtest.py`

**路由注册** (在 `main.py` 中):
```python
app.include_router(indicators.router)
app.include_router(stocks.router)
```

## 数据库规范

**ORM**: SQLAlchemy 2.0
**数据库**: SQLite (`stock_monitor.db`)

**模型定义** (`backend/app/database.py`):
```python
class SignalAlert(Base):
    __tablename__ = "signal_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), index=True)
    created_at = Column(DateTime, default=datetime.now)
```

## WebSocket 通信规范

**路径**: `/ws`
**心跳**: 30秒间隔发送 `{"type": "ping"}`
**消息格式**:
```javascript
// 指标更新
{ type: "indicators", data: { ... } }

// 信号提醒
{ type: "signal", data: { signal_type, signal_count, details } }
```

## 文件组织

```
backend/
  app/
    routers/          # API路由
    services/         # 业务逻辑
    database.py       # 数据库模型
    main.py          # FastAPI入口
  run.py             # 启动脚本

frontend/
  src/
    components/       # Vue组件
    views/           # 页面视图
    services/        # API服务
    router/          # 路由配置
  App.vue           # 根组件
  main.js           # 入口文件
```

## 修改前必读

1. 先阅读相关文件了解上下文
2. 不确定时先询问，不要猜测
3. 每次只做最小必要的修改
4. 修改后检查前后端是否正常运行
5. 保持中文注释风格
