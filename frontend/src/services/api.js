// API服务
const API_BASE = '/api'
const WS_URL = `ws://${window.location.host}/ws`

// HTTP请求
const request = async (url, options = {}) => {
  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  })
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  
  return response.json()
}

export const api = {
  // 获取当前指标
  getIndicators: () => request('/indicators/current'),
  
  // 获取警报历史
  getAlerts: (limit = 20) => request(`/indicators/alerts?limit=${limit}`),
  
  // 切换股票
  switchStock: (code, name = '') => request('/indicators/switch', {
    method: 'POST',
    body: JSON.stringify({ code, name })
  }),
  
  // 获取实时行情
  getQuote: (code) => request(`/indicators/quote?code=${code}`),
  
  // 获取股票列表
  getStocks: () => request('/stocks/')
}

// WebSocket服务
export const ws = {
  connection: null,
  heartbeatInterval: null,
  
  connect(onMessage, onConnect, onDisconnect) {
    const wsUrl = WS_URL
    this.connection = new WebSocket(wsUrl)
    
    this.connection.onopen = () => {
      console.log('WebSocket已连接')
      if (onConnect) onConnect()
      
      // 启动心跳
      this.heartbeatInterval = setInterval(() => {
        if (this.connection && this.connection.readyState === WebSocket.OPEN) {
          this.connection.send(JSON.stringify({ type: 'ping' }))
        }
      }, 30000)
    }
    
    this.connection.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        if (message.type !== 'pong') {
          console.log('收到消息:', message)
        }
        if (onMessage) onMessage(message)
      } catch (error) {
        console.error('解析消息失败:', error)
      }
    }
    
    this.connection.onclose = () => {
      console.log('WebSocket已关闭')
      if (this.heartbeatInterval) {
        clearInterval(this.heartbeatInterval)
      }
      if (onDisconnect) onDisconnect()
    }
    
    this.connection.onerror = (error) => {
      console.error('WebSocket错误:', error)
    }
    
    return this.connection
  },
  
  close() {
    if (this.connection) {
      this.connection.close()
    }
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
    }
  }
}
