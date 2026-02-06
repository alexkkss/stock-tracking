<template>
  <div class="backtest-page">
    <el-page-header title="返回" @back="$router.push('/')">
      <template #content>
        <span class="page-title">策略回测</span>
      </template>
    </el-page-header>

    <!-- 回测配置 -->
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>回测配置</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="120px">
        <el-form-item label="股票代码">
          <el-input 
            v-model="form.stock_code" 
            placeholder="输入6位股票代码"
            style="width: 200px"
          >
            <template #prepend>股票</template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="选择指标组合">
          <el-checkbox-group v-model="form.indicators">
            <el-checkbox 
              v-for="ind in availableIndicators" 
              :key="ind.key" 
              :label="ind.key"
              border
            >
              {{ ind.name }}
              <el-tooltip :content="ind.description" placement="top">
                <el-icon><QuestionFilled /></el-icon>
              </el-tooltip>
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="信号条件">
          <el-radio-group v-model="form.signal_mode">
            <el-radio label="all">全部满足（{{ form.indicators.length }}个指标同时发出信号）</el-radio>
            <el-radio label="custom">自定义</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item v-if="form.signal_mode === 'custom'" label="最少信号数">
          <el-slider 
            v-model="form.min_buy_signals" 
            :max="form.indicators.length"
            :min="1"
            show-stops
          />
          <span class="slider-value">{{ form.min_buy_signals }}个指标</span>
        </el-form-item>
        
        <el-form-item label="持有天数">
          <el-slider v-model="form.hold_days" :max="30" :min="1" show-stops />
          <span class="slider-value">{{ form.hold_days }}天</span>
        </el-form-item>
        
        <el-form-item label="回测周期">
          <el-slider v-model="form.days_history" :max="1095" :min="30" :step="30" show-stops />
          <span class="slider-value">{{ form.days_history }}天（约{{ Math.round(form.days_history/365) }}年）</span>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="runBacktest" :loading="loading" size="large">
            <el-icon><Search /></el-icon>
            开始回测
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 回测结果 -->
    <el-card v-if="result" class="result-card">
      <template #header>
        <div class="card-header">
          <span>回测结果</span>
          <el-tag :type="result.win_rate >= 50 ? 'success' : 'danger'" effect="dark" size="large">
            胜率 {{ result.win_rate }}%
          </el-tag>
        </div>
      </template>
      
      <!-- 统计卡片 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :span="4">
          <div class="stat-box">
            <div class="stat-label">总信号次数</div>
            <div class="stat-value">{{ result.total_signals }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-box win">
            <div class="stat-label">盈利次数</div>
            <div class="stat-value">{{ result.win_count }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-box loss">
            <div class="stat-label">亏损次数</div>
            <div class="stat-value">{{ result.loss_count }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-box">
            <div class="stat-label">平均收益</div>
            <div class="stat-value" :class="result.avg_return >= 0 ? 'up' : 'down'">
              {{ result.avg_return >= 0 ? '+' : '' }}{{ result.avg_return }}%
            </div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-box">
            <div class="stat-label">最大盈利</div>
            <div class="stat-value up">+{{ result.max_return }}%</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-box">
            <div class="stat-label">最大亏损</div>
            <div class="stat-value down">{{ result.min_return }}%</div>
          </div>
        </el-col>
      </el-row>

      <!-- 收益率分布图 -->
      <div class="chart-section" v-if="result.trades.length > 0">
        <h4>收益率分布</h4>
        <div class="returns-chart">
          <div 
            v-for="(trade, index) in result.trades" 
            :key="index"
            class="return-bar"
            :class="trade.return_pct >= 0 ? 'up' : 'down'"
            :style="{ height: Math.abs(trade.return_pct) * 3 + 'px' }"
            :title="`${trade.buy_date}: ${trade.return_pct}%`"
          />
        </div>
      </div>

      <!-- 交易记录表格 -->
      <h4 class="table-title">交易记录（{{ result.trades.length }}笔）</h4>
      <el-table :data="result.trades" style="width: 100%" height="400" border>
        <el-table-column type="index" width="50" />
        <el-table-column prop="buy_date" label="买入日期" width="120" />
        <el-table-column prop="sell_date" label="卖出日期" width="120" />
        <el-table-column prop="buy_price" label="买入价" width="100">
          <template #default="scope">
            ¥{{ scope.row.buy_price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="sell_price" label="卖出价" width="100">
          <template #default="scope">
            ¥{{ scope.row.sell_price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="return_pct" label="收益率" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.return_pct >= 0 ? 'success' : 'danger'" effect="dark">
              {{ scope.row.return_pct >= 0 ? '+' : '' }}{{ scope.row.return_pct }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="signals" label="信号数" width="80" />
      </el-table>
    </el-card>

    <!-- 空状态 -->
    <el-empty v-else-if="!loading" description="配置参数后点击开始回测" />
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, QuestionFilled } from '@element-plus/icons-vue'

export default {
  name: 'Backtest',
  components: {
    Search,
    QuestionFilled
  },
  setup() {
    const loading = ref(false)
    const availableIndicators = ref([])
    const result = ref(null)
    
    const form = reactive({
      stock_code: '600489',
      indicators: ['macd', 'kdj', 'rsi'],
      signal_mode: 'all',
      min_buy_signals: 3,
      hold_days: 5,
      days_history: 365
    })

    // 获取可用指标
    const fetchIndicators = async () => {
      try {
        const response = await fetch('/api/backtest/indicators')
        availableIndicators.value = await response.json()
      } catch (error) {
        console.error('获取指标列表失败:', error)
      }
    }

    // 运行回测
    const runBacktest = async () => {
      if (form.indicators.length === 0) {
        ElMessage.warning('请至少选择一个指标')
        return
      }

      loading.value = true
      result.value = null

      try {
        const requestData = {
          stock_code: form.stock_code,
          indicators: form.indicators,
          hold_days: form.hold_days,
          days_history: form.days_history,
          min_buy_signals: form.signal_mode === 'all' ? form.indicators.length : form.min_buy_signals
        }

        const response = await fetch('/api/backtest/run', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        })

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || '回测失败')
        }

        result.value = await response.json()
        ElMessage.success('回测完成')
      } catch (error) {
        ElMessage.error(error.message || '回测失败')
        console.error(error)
      } finally {
        loading.value = false
      }
    }

    // 重置表单
    const resetForm = () => {
      form.stock_code = '600489'
      form.indicators = ['macd', 'kdj', 'rsi']
      form.signal_mode = 'all'
      form.min_buy_signals = 3
      form.hold_days = 5
      form.days_history = 365
      result.value = null
    }

    onMounted(() => {
      fetchIndicators()
    })

    return {
      form,
      loading,
      availableIndicators,
      result,
      runBacktest,
      resetForm
    }
  }
}
</script>

<style scoped>
.backtest-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.config-card {
  margin: 20px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.slider-value {
  margin-left: 15px;
  color: #606266;
  font-weight: 500;
}

.result-card {
  margin-top: 20px;
}

.stats-row {
  margin-bottom: 30px;
}

.stat-box {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  border: 1px solid #e4e7ed;
}

.stat-box.win {
  background: #f0f9ff;
  border-color: #67c23a;
}

.stat-box.loss {
  background: #fef0f0;
  border-color: #f56c6c;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-value.up {
  color: #f56c6c;
}

.stat-value.down {
  color: #67c23a;
}

.chart-section {
  margin: 30px 0;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.chart-section h4 {
  margin: 0 0 20px 0;
  color: #303133;
}

.returns-chart {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  height: 150px;
  padding: 20px 0;
  overflow-x: auto;
}

.return-bar {
  width: 12px;
  min-width: 12px;
  border-radius: 2px 2px 0 0;
  transition: all 0.3s;
}

.return-bar.up {
  background: #f56c6c;
}

.return-bar.down {
  background: #67c23a;
  border-radius: 0 0 2px 2px;
}

.return-bar:hover {
  opacity: 0.8;
  transform: scaleX(1.3);
}

.table-title {
  margin: 30px 0 20px 0;
  color: #303133;
}
</style>