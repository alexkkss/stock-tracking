<template>
  <div class="app">
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <div class="left-section">
            <h1 class="title">
              <el-icon><TrendCharts /></el-icon>
              股票监控系统
            </h1>
            <el-menu
              :default-active="$route.path"
              mode="horizontal"
              router
              class="nav-menu"
            >
              <el-menu-item index="/">
                <el-icon><Monitor /></el-icon>
                实时监控
              </el-menu-item>
              <el-menu-item index="/backtest">
                <el-icon><DataAnalysis /></el-icon>
                策略回测
              </el-menu-item>
            </el-menu>
          </div>
          <div class="connection-status">
            <el-tag :type="wsConnected ? 'success' : 'danger'" effect="dark">
              <el-icon v-if="wsConnected"><Connection /></el-icon>
              <el-icon v-else><Warning /></el-icon>
              {{ wsConnected ? '已连接' : '未连接' }}
            </el-tag>
          </div>
        </div>
      </el-header>
      
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
    
    <!-- 信号提醒弹窗 -->
    <SignalAlert 
      v-model:visible="alertVisible" 
      :signal="latestSignal"
    />
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted, provide } from 'vue'
import { useRoute } from 'vue-router'
import SignalAlert from './components/SignalAlert.vue'
import { api, ws } from './services/api'

export default {
  name: 'App',
  components: {
    SignalAlert
  },
  setup() {
    const route = useRoute()
    const wsConnected = ref(false)
    const currentIndicators = ref(null)
    const recentAlerts = ref([])
    const currentStock = reactive({
      code: '600489',
      name: '中金黄金'
    })
    const alertVisible = ref(false)
    const latestSignal = ref(null)
    
    let wsConnection = null
    
    // WebSocket消息处理
    const handleWebSocketMessage = (message) => {
      if (message.type === 'indicators') {
        currentIndicators.value = message.data
      } else if (message.type === 'signal') {
        latestSignal.value = message.data
        alertVisible.value = true
        // 刷新警报列表
        fetchAlerts()
      }
    }
    
    // 获取初始数据
    const fetchInitialData = async () => {
      try {
        const indicators = await api.getIndicators()
        currentIndicators.value = indicators
        
        const alerts = await api.getAlerts()
        recentAlerts.value = alerts
      } catch (error) {
        console.error('获取初始数据失败:', error)
      }
    }
    
    // 获取警报列表
    const fetchAlerts = async () => {
      try {
        const alerts = await api.getAlerts()
        recentAlerts.value = alerts
      } catch (error) {
        console.error('获取警报失败:', error)
      }
    }
    
    // 切换股票
    const switchStock = async (code, name) => {
      try {
        await api.switchStock(code, name)
        currentStock.code = code
        currentStock.name = name
        // 刷新数据
        fetchInitialData()
      } catch (error) {
        console.error('切换股票失败:', error)
      }
    }
    
    // 连接WebSocket
    const connectWebSocket = () => {
      wsConnection = ws.connect(
        // onMessage
        (message) => {
          handleWebSocketMessage(message)
        },
        // onConnect
        () => {
          wsConnected.value = true
        },
        // onDisconnect
        () => {
          wsConnected.value = false
          // 3秒后重连
          setTimeout(connectWebSocket, 3000)
        }
      )
    }
    
    onMounted(() => {
      fetchInitialData()
      connectWebSocket()
    })
    
    onUnmounted(() => {
      if (wsConnection) {
        wsConnection.close()
      }
    })
    
    // 提供给子组件
    provide('stockData', {
      currentStock,
      currentIndicators,
      recentAlerts,
      switchStock
    })
    
    return {
      route,
      wsConnected,
      alertVisible,
      latestSignal
    }
  }
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: #f5f7fa;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.left-section {
  display: flex;
  align-items: center;
  gap: 40px;
}

.title {
  margin: 0;
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #303133;
}

.nav-menu {
  border-bottom: none;
}

.connection-status {
  display: flex;
  align-items: center;
}

.main {
  padding: 20px;
}
</style>