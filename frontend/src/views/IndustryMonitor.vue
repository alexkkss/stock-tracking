<template>
  <div class="industry-monitor">
    <el-card class="control-panel">
      <div class="control-row">
        <div class="left-section">
          <span class="label">当前股票行业:</span>
          <el-tag v-if="currentIndustry" type="success" size="large" effect="dark">
            {{ currentIndustry }}
          </el-tag>
          <el-tag v-else type="info" size="large">未获取</el-tag>
          
          <el-divider direction="vertical" />
          
          <span class="label">选择行业:</span>
          <el-select 
            v-model="selectedIndustry" 
            placeholder="请选择行业" 
            style="width: 200px"
            @change="handleIndustryChange"
          >
            <el-option
              v-for="industry in industries"
              :key="industry"
              :label="industry"
              :value="industry"
            />
          </el-select>
        </div>
        
        <div class="right-section">
          <span class="label">排序方式:</span>
          <el-radio-group v-model="sortBy" @change="handleSortChange">
            <el-radio-button label="change">涨跌幅</el-radio-button>
            <el-radio-button label="volume">成交量</el-radio-button>
            <el-radio-button label="amount">成交额</el-radio-button>
          </el-radio-group>
          
          <el-button 
            type="primary" 
            :icon="Refresh"
            :loading="loading"
            @click="refreshData"
            style="margin-left: 15px"
          >
            刷新
          </el-button>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20" class="content-area">
      <!-- 左侧：股票列表 -->
      <el-col :span="10">
        <el-card class="stock-list">
          <template #header>
            <div class="card-header">
              <span>股票排行</span>
              <el-tag size="small" type="info">共 {{ totalCount }} 只</el-tag>
            </div>
          </template>

          <!-- 涨幅前10 -->
          <div class="list-section">
            <div class="section-title">
              <el-icon color="#67C23A"><Top /></el-icon>
              <span>涨幅前10</span>
            </div>
            <el-table 
              :data="topGainers" 
              style="width: 100%" 
              size="small"
              :row-class-name="tableRowClassName"
            >
              <el-table-column prop="code" label="代码" width="80" />
              <el-table-column prop="name" label="名称" width="100" />
              <el-table-column prop="price" label="最新价" width="80">
                <template #default="{ row }">
                  <span :class="getPriceClass(row.change)">{{ row.price.toFixed(2) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="change" label="涨跌幅" width="90">
                <template #default="{ row }">
                  <span :class="getChangeClass(row.change)">
                    {{ row.change > 0 ? '+' : '' }}{{ row.change.toFixed(2) }}%
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="volume" label="成交量">
                <template #default="{ row }">
                  {{ formatVolume(row.volume) }}
                </template>
              </el-table-column>
            </el-table>
          </div>

          <el-divider />

          <!-- 跌幅前10 -->
          <div class="list-section">
            <div class="section-title">
              <el-icon color="#F56C6C"><Bottom /></el-icon>
              <span>跌幅前10</span>
            </div>
            <el-table 
              :data="topLosers" 
              style="width: 100%" 
              size="small"
              :row-class-name="tableRowClassName"
            >
              <el-table-column prop="code" label="代码" width="80" />
              <el-table-column prop="name" label="名称" width="100" />
              <el-table-column prop="price" label="最新价" width="80">
                <template #default="{ row }">
                  <span :class="getPriceClass(row.change)">{{ row.price.toFixed(2) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="change" label="涨跌幅" width="90">
                <template #default="{ row }">
                  <span :class="getChangeClass(row.change)">
                    {{ row.change > 0 ? '+' : '' }}{{ row.change.toFixed(2) }}%
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="volume" label="成交量">
                <template #default="{ row }">
                  {{ formatVolume(row.volume) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：图表对比 -->
      <el-col :span="14">
        <el-card class="chart-panel">
          <template #header>
            <div class="card-header">
              <span>成交量对比</span>
              <span class="update-time" v-if="updateTime">更新时间: {{ formatTime(updateTime) }}</span>
            </div>
          </template>

          <!-- 成交量柱状图 -->
          <div ref="volumeChartRef" class="chart-container" style="height: 400px;"></div>
        </el-card>

        <el-card class="chart-panel" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>涨跌幅对比</span>
            </div>
          </template>

          <!-- 涨跌幅条形图 -->
          <div ref="changeChartRef" class="chart-container" style="height: 400px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, inject, nextTick } from 'vue'
import { Top, Bottom, Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { api } from '../services/api'

export default {
  name: 'IndustryMonitor',
  components: {
    Top,
    Bottom,
    Refresh
  },
  setup() {
    // 注入当前股票数据
    const stockData = inject('stockData')
    const currentStock = stockData?.currentStock || { code: '600489', name: '中金黄金' }

    // 状态
    const industries = ref([])
    const selectedIndustry = ref('')
    const currentIndustry = ref('')
    const sortBy = ref('change')
    const loading = ref(false)
    const totalCount = ref(0)
    const updateTime = ref('')
    
    const topGainers = ref([])
    const topLosers = ref([])
    
    // 图表实例
    let volumeChart = null
    let changeChart = null
    const volumeChartRef = ref(null)
    const changeChartRef = ref(null)

    // 获取行业列表
    const fetchIndustries = async () => {
      try {
        const data = await api.getIndustries()
        industries.value = data.industries || []
      } catch (error) {
        console.error('获取行业列表失败:', error)
      }
    }

    // 获取当前股票所属行业
    const fetchCurrentStockIndustry = async () => {
      try {
        const data = await api.getStockIndustry(currentStock.code)
        if (data.industry) {
          currentIndustry.value = data.industry
          selectedIndustry.value = data.industry
          // 自动加载该行业数据
          await fetchIndustryStocks(data.industry)
        }
      } catch (error) {
        console.error('获取当前股票行业失败:', error)
      }
    }

    // 获取行业股票数据
    const fetchIndustryStocks = async (industry) => {
      if (!industry) return
      
      loading.value = true
      try {
        const data = await api.getIndustryStocks(industry, sortBy.value)
        topGainers.value = data.top_gainers || []
        topLosers.value = data.top_losers || []
        totalCount.value = data.total_count || 0
        updateTime.value = data.update_time
        
        // 更新图表
        nextTick(() => {
          updateCharts()
        })
      } catch (error) {
        console.error('获取行业股票失败:', error)
      } finally {
        loading.value = false
      }
    }

    // 处理行业切换
    const handleIndustryChange = (industry) => {
      if (industry) {
        fetchIndustryStocks(industry)
      }
    }

    // 处理排序方式切换
    const handleSortChange = () => {
      if (selectedIndustry.value) {
        fetchIndustryStocks(selectedIndustry.value)
      }
    }

    // 刷新数据
    const refreshData = () => {
      if (selectedIndustry.value) {
        fetchIndustryStocks(selectedIndustry.value)
      }
    }

    // 更新图表
    const updateCharts = () => {
      updateVolumeChart()
      updateChangeChart()
    }

    // 更新成交量图表
    const updateVolumeChart = () => {
      if (!volumeChartRef.value) return
      
      if (!volumeChart) {
        volumeChart = echarts.init(volumeChartRef.value)
      }

      // 合并前10和后10的数据
      const allStocks = [...topGainers.value, ...topLosers.value]
      
      const codes = allStocks.map(s => s.name)
      const volumes = allStocks.map(s => s.volume / 10000) // 转换为万手
      const colors = allStocks.map(s => s.change >= 0 ? '#67C23A' : '#F56C6C')

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: (params) => {
            const stock = allStocks[params[0].dataIndex]
            return `${stock.name}<br/>
                    成交量: ${formatVolume(stock.volume)}<br/>
                    涨跌幅: ${stock.change > 0 ? '+' : ''}${stock.change.toFixed(2)}%`
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: codes,
          axisLabel: {
            rotate: 45,
            fontSize: 11
          }
        },
        yAxis: {
          type: 'value',
          name: '成交量(万手)',
          nameTextStyle: {
            fontSize: 11
          }
        },
        series: [{
          data: volumes.map((val, idx) => ({
            value: val,
            itemStyle: { color: colors[idx] }
          })),
          type: 'bar',
          barWidth: '60%'
        }]
      }

      volumeChart.setOption(option)
    }

    // 更新涨跌幅图表
    const updateChangeChart = () => {
      if (!changeChartRef.value) return
      
      if (!changeChart) {
        changeChart = echarts.init(changeChartRef.value)
      }

      // 合并前10和后10的数据，按涨跌幅排序
      const allStocks = [...topGainers.value, ...topLosers.value]
        .sort((a, b) => b.change - a.change)
      
      const codes = allStocks.map(s => s.name)
      const changes = allStocks.map(s => s.change)
      const colors = changes.map(c => c >= 0 ? '#67C23A' : '#F56C6C')

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: (params) => {
            const stock = allStocks[params[0].dataIndex]
            return `${stock.name}<br/>
                    涨跌幅: ${stock.change > 0 ? '+' : ''}${stock.change.toFixed(2)}%<br/>
                    最新价: ${stock.price.toFixed(2)}`
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          name: '涨跌幅(%)',
          nameTextStyle: {
            fontSize: 11
          },
          axisLabel: {
            formatter: '{value}%'
          }
        },
        yAxis: {
          type: 'category',
          data: codes,
          axisLabel: {
            fontSize: 11
          }
        },
        series: [{
          data: changes.map((val, idx) => ({
            value: val,
            itemStyle: { color: colors[idx] }
          })),
          type: 'bar',
          barWidth: '60%',
          label: {
            show: true,
            position: 'right',
            formatter: (params) => {
              return (params.value > 0 ? '+' : '') + params.value.toFixed(2) + '%'
            },
            fontSize: 10
          }
        }]
      }

      changeChart.setOption(option)
    }

    // 格式化成交量
    const formatVolume = (volume) => {
      if (volume >= 100000000) {
        return (volume / 100000000).toFixed(2) + '亿'
      } else if (volume >= 10000) {
        return (volume / 10000).toFixed(2) + '万'
      }
      return volume.toString()
    }

    // 格式化时间
    const formatTime = (timeStr) => {
      if (!timeStr) return ''
      const date = new Date(timeStr)
      return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    }

    // 获取价格样式类
    const getPriceClass = (change) => {
      return change >= 0 ? 'price-up' : 'price-down'
    }

    // 获取涨跌幅样式类
    const getChangeClass = (change) => {
      return change >= 0 ? 'change-up' : 'change-down'
    }

    // 表格行样式
    const tableRowClassName = ({ row }) => {
      return row.change >= 0 ? 'row-up' : 'row-down'
    }

    // 窗口大小改变时重新渲染图表
    const handleResize = () => {
      volumeChart?.resize()
      changeChart?.resize()
    }

    onMounted(() => {
      fetchIndustries()
      fetchCurrentStockIndustry()
      window.addEventListener('resize', handleResize)
    })

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
      volumeChart?.dispose()
      changeChart?.dispose()
    })

    return {
      industries,
      selectedIndustry,
      currentIndustry,
      sortBy,
      loading,
      totalCount,
      updateTime,
      topGainers,
      topLosers,
      volumeChartRef,
      changeChartRef,
      handleIndustryChange,
      handleSortChange,
      refreshData,
      formatVolume,
      formatTime,
      getPriceClass,
      getChangeClass,
      tableRowClassName,
      Refresh
    }
  }
}
</script>

<style scoped>
.industry-monitor {
  padding: 20px;
}

.control-panel {
  margin-bottom: 20px;
}

.control-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.left-section, .right-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.label {
  font-weight: 500;
  color: #606266;
}

.content-area {
  margin-top: 0;
}

.stock-list {
  height: calc(100vh - 250px);
  overflow-y: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.update-time {
  font-size: 12px;
  color: #909399;
  font-weight: normal;
}

.list-section {
  margin-bottom: 15px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: 600;
  margin-bottom: 10px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
}

.chart-panel {
  height: calc(50vh - 140px);
}

.chart-container {
  width: 100%;
  height: 100%;
}

/* 价格样式 */
.price-up, .change-up {
  color: #67C23A;
  font-weight: 600;
}

.price-down, .change-down {
  color: #F56C6C;
  font-weight: 600;
}

/* 表格行样式 */
:deep(.row-up) {
  background-color: rgba(103, 194, 58, 0.05);
}

:deep(.row-down) {
  background-color: rgba(245, 108, 108, 0.05);
}
</style>
