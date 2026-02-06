# A股股票监控系统

## 功能特性

- 实时监控A股技术指标（MACD、KDJ、RSI、均线、成交量、布林带）
- 多重信号共振检测（≥4个同向指标触发提醒）
- WebSocket实时推送，前端弹窗提醒
- 股票切换功能
- 信号历史记录

## 系统架构

```
前端 (Vue 3)  <--WebSocket-->  后端 (FastAPI)
     |                              |
     v                              v
仪表盘展示                   指标计算引擎
信号弹窗提醒                 akshare数据获取
                            SQLite数据存储
```

## 快速启动

### 1. 安装后端依赖

```bash
cd stock-monitor/backend
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
python run.py
```

后端将运行在 http://localhost:8000

### 3. 安装前端依赖（新终端）

```bash
cd stock-monitor/frontend
npm install
```

### 4. 启动前端服务

```bash
npm run dev
```

前端将运行在 http://localhost:3000

## 使用方法

1. 打开浏览器访问 http://localhost:3000
2. 系统默认监控 **中金黄金(600489)**
3. 查看实时6大技术指标状态
4. 当≥4个指标同时发出买入/卖出信号时，会弹出提醒窗口
5. 可在顶部输入框切换监控其他股票（输入6位数字代码）

## 指标说明

| 指标 | 买入信号 | 卖出信号 |
|------|---------|---------|
| MACD | 金叉 | 死叉 |
| KDJ | 金叉(K<20) | 死叉(K>80) |
| RSI | 超卖(<30) | 超买(>70) |
| 均线 | 金叉 | 死叉 |
| 成交量 | 放量 | 缩量 |
| 布林带 | 下轨反弹 | 上轨回落 |

## API接口

- `GET /api/indicators/current` - 获取当前指标
- `POST /api/indicators/switch` - 切换监控股票
- `GET /api/indicators/alerts` - 获取信号历史
- `WebSocket /ws` - 实时数据推送

## 注意事项

1. 仅A股开市时间（9:30-11:30, 13:00-15:00）有实时数据
2. 非交易时间显示最近交易日数据
3. 切换股票后，指标需要重新计算
4. 信号触发后会保存到本地SQLite数据库

## 技术栈

- **后端**: Python + FastAPI + SQLAlchemy + APScheduler
- **前端**: Vue 3 + Element Plus + WebSocket
- **数据源**: akshare（免费A股数据）
- **数据库**: SQLite（本地轻量存储）