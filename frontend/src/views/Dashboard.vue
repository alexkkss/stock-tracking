<template>
  <div class="dashboard">
    <!-- 股票信息卡片 -->
    <el-card class="stock-card">
      <div class="stock-header">
        <div class="stock-info">
          <h2>{{ stockName }} ({{ stockCode }})</h2>
          <div class="price-info" v-if="indicators">
            <span class="current-price">¥{{ indicators.price?.toFixed(2) }}</span>
            <span class="change-rate" :class="getChangeClass(indicators.change_pct)">
              {{ indicators.change_pct > 0 ? '+' : '' }}{{ indicators.change_pct?.toFixed(2) }}%
            </span>
          </div>
        </div>
        <div class="stock-actions">
          <el-input
            v-model="newStockCode"
            placeholder="输入股票代码"
            style="width: 150px"
            size="large"
          >
            <template #append>
              <el-button @click="switchStock" :icon="Search" />
            </template>
          </el-input>
        </div>
      </div>
      
      <div class="signal-summary" v-if="indicators">
        <div class="signal-box buy">
          <div class="signal-label">买入信号</div>
          <div class="signal-value">{{ indicators.buy_signals }}</div>
        </div>
        <div class="signal-divider">VS</div>
        <div class="signal-box sell">
          <div class="signal-label">卖出信号</div>
          <div class="signal-value">{{ indicators.sell_signals }}</div>
        </div>
      </div>
      
      <div class="final-signal" v-if="indicators">
        <el-tag 
          :type="getFinalSignalType(indicators.final_signal)"
          effect="dark"
          size="large"
          class="final-tag"
        >
          {{ getFinalSignalText(indicators.final_signal) }}
        </el-tag>
      </div>
    </el-card>

    <!-- 指标卡片网格 -->
    <el-row :gutter="20" class="indicator-grid">
      <el-col :span="8" v-for="(item, key) in indicatorList" :key="key">
        <el-card 
          class="indicator-card"
          :class="getIndicatorClass(item)"
        >
          <div class="indicator-header">
            <span class="indicator-name">{{ item.name }}</span>
            <el-tag 
              :type="getSignalType(item.signal)"
              size="small"
              effect="dark"
            >
              {{ item.signal }}
            </el-tag>
          </div>
          <div class="indicator-values">
            <div v-for="(val, k) in item.values" :key="k" class="value-item">
              <span class="value-label">{{ k }}:</span>
              <span class="value-num">{{ formatValue(val) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 信号历史 -->
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <span>信号历史</span>
          <el-tag type="info">最近20条</el-tag>
        </div>
      </template>
      
      <el-table :data="alerts" style="width: 100%">
        <el-table-column prop="timestamp" label="时间" width="180">
          <template #default="scope">
            {{ formatTime(scope.row.timestamp) }}
          </template>
        </el-table-column>
        <el-table-column prop="signal_type" label="信号类型" width="120">
          <template #default="scope">
            <el-tag 
              :type="scope.row.signal_type === 'BUY' ? 'success' : 'danger'"
              effect="dark"
            >
              {{ scope.row.signal_type === 'BUY' ? '买入' : '卖出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="signal_count" label="指标数" width="100" />
        <el-table-column prop="price" label="价格" width="120">
          <template #default="scope">
            ¥{{ scope.row.price?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="details" label="详情" />
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { ref, computed, inject } from 'vue'
import { Search } from '@element-plus/icons-vue'

export default {
  name: 'Dashboard',
  setup() {
    const newStockCode = ref('')
    const stockData = inject('stockData')
    
    const indicators = computed(() => stockData?.currentIndicators?.value)
    const alerts = computed(() => stockData?.recentAlerts?.value || [])
    const stockCode = computed(() => stockData?.currentStock?.code || '600489')
    const stockName = computed(() => stockData?.currentStock?.name || '中金黄金')

    const indicatorList = computed(() => {
      if (!indicators.value || !indicators.value.indicators) return []
      
      const ind = indicators.value.indicators
      return [
        {
          name: 'MACD',
          signal: ind.macd?.signal,
          values: {
            DIF: ind.macd?.dif,
            DEA: ind.macd?.dea,
            MACD: ind.macd?.macd
          }
        },
        {
          name: 'KDJ',
          signal: ind.kdj?.signal,
          values: {
            K: ind.kdj?.k,
            D: ind.kdj?.d,
            J: ind.kdj?.j
          }
        },
        {
          name: 'RSI',
          signal: ind.rsi?.signal,
          values: {
            数值: ind.rsi?.value
          }
        },
        {
          name: '均线',
          signal: ind.ma?.signal,
          values: {
            MA5: ind.ma?.ma5,
            MA10: ind.ma?.ma10,
            MA20: ind.ma?.ma20
          }
        },
        {
          name: '成交量',
          signal: ind.volume?.signal,
          values: {
            当前: ind.volume?.current,
            MA5: ind.volume?.ma5
          }
        },
        {
          name: '布林带',
          signal: ind.boll?.signal,
          values: {
            上轨: ind.boll?.upper,
            中轨: ind.boll?.middle,
            下轨: ind.boll?.lower
          }
        }
      ]
    })

    const switchStock = () => {
      if (newStockCode.value && stockData?.switchStock) {
        stockData.switchStock(newStockCode.value, '')
        newStockCode.value = ''
      }
    }

    const getChangeClass = (change) => {
      if (change > 0) return 'up'
      if (change < 0) return 'down'
      return ''
    }

    const getFinalSignalType = (signal) => {
      if (signal === 'BUY') return 'success'
      if (signal === 'SELL') return 'danger'
      return 'info'
    }

    const getFinalSignalText = (signal) => {
      if (signal === 'BUY') return '买入信号'
      if (signal === 'SELL') return '卖出信号'
      return '持有观望'
    }

    const getIndicatorClass = (item) => {
      if (item.signal === '金叉' || item.signal === '超卖' || item.signal === '下轨反弹' || item.signal === '放量') {
        return 'buy-signal'
      }
      if (item.signal === '死叉' || item.signal === '超买' || item.signal === '上轨回落' || item.signal === '缩量') {
        return 'sell-signal'
      }
      return ''
    }

    const getSignalType = (signal) => {
      if (['金叉', '超卖', '下轨反弹', '放量'].includes(signal)) return 'success'
      if (['死叉', '超买', '上轨回落', '缩量'].includes(signal)) return 'danger'
      return 'info'
    }

    const formatValue = (val) => {
      if (typeof val === 'number') {
        if (Math.abs(val) >= 1000000) {
          return (val / 10000).toFixed(2) + '万'
        }
        return val.toFixed(2)
      }
      return val
    }

    const formatTime = (timestamp) => {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      return date.toLocaleString('zh-CN')
    }

    return {
      newStockCode,
      Search,
      indicators,
      alerts,
      stockCode,
      stockName,
      indicatorList,
      switchStock,
      getChangeClass,
      getFinalSignalType,
      getFinalSignalText,
      getIndicatorClass,
      getSignalType,
      formatValue,
      formatTime
    }
  }
}
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.stock-card {
  margin-bottom: 20px;
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.stock-info h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
  color: #303133;
}

.price-info {
  display: flex;
  align-items: baseline;
  gap: 15px;
}

.current-price {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.change-rate {
  font-size: 18px;
  font-weight: bold;
}

.change-rate.up {
  color: #f56c6c;
}

.change-rate.down {
  color: #67c23a;
}

.signal-summary {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 40px;
  padding: 20px 0;
  border-top: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
}

.signal-box {
  text-align: center;
  padding: 15px 30px;
  border-radius: 8px;
}

.signal-box.buy {
  background: #f0f9ff;
  border: 2px solid #67c23a;
}

.signal-box.sell {
  background: #fef0f0;
  border: 2px solid #f56c6c;
}

.signal-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
}

.signal-value {
  font-size: 36px;
  font-weight: bold;
}

.signal-box.buy .signal-value {
  color: #67c23a;
}

.signal-box.sell .signal-value {
  color: #f56c6c;
}

.signal-divider {
  font-size: 18px;
  color: #909399;
  font-weight: bold;
}

.final-signal {
  text-align: center;
  margin-top: 20px;
}

.final-tag {
  font-size: 18px;
  padding: 10px 30px;
}

.indicator-grid {
  margin-bottom: 20px;
}

.indicator-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.indicator-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.indicator-card.buy-signal {
  border: 2px solid #67c23a;
  background: #f0f9ff;
}

.indicator-card.sell-signal {
  border: 2px solid #f56c6c;
  background: #fef0f0;
}

.indicator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.indicator-name {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.indicator-values {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.value-item {
  display: flex;
  gap: 5px;
  font-size: 14px;
}

.value-label {
  color: #909399;
}

.value-num {
  color: #606266;
  font-weight: 500;
}

.history-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>