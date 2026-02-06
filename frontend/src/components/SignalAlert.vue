<template>
  <el-dialog
    v-model="dialogVisible"
    :title="title"
    width="400px"
    :show-close="false"
    :close-on-click-modal="false"
    class="signal-alert-dialog"
  >
    <div class="alert-content" :class="signalType">
      <div class="icon-wrapper">
        <el-icon size="60" v-if="signalType === 'buy'">
          <Top />
        </el-icon>
        <el-icon size="60" v-else>
          <Bottom />
        </el-icon>
      </div>
      
      <div class="signal-info">
        <h2>{{ signal?.stock_name || signal?.stock_code }}</h2>
        <p class="price">当前价格: ¥{{ signal?.price?.toFixed(2) }}</p>
        <p class="signal-count">{{ signal?.signal_count }}个指标共振</p>
      </div>
      
      <div class="indicator-tags">
        <el-tag 
          v-for="(count, type) in signalCounts" 
          :key="type"
          :type="type === 'buy' ? 'success' : 'danger'"
          effect="dark"
          size="large"
        >
          {{ type === 'buy' ? '买入' : '卖出' }}信号: {{ count }}个
        </el-tag>
      </div>
    </div>
    
    <template #footer>
      <el-button type="primary" @click="closeDialog" size="large">
        知道了
      </el-button>
    </template>
  </el-dialog>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'SignalAlert',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    signal: {
      type: Object,
      default: null
    }
  },
  emits: ['update:visible'],
  setup(props, { emit }) {
    const dialogVisible = computed({
      get: () => props.visible,
      set: (val) => emit('update:visible', val)
    })
    
    const signalType = computed(() => {
      return props.signal?.final_signal === 'BUY' ? 'buy' : 'sell'
    })
    
    const title = computed(() => {
      return signalType.value === 'buy' ? '买入信号提醒' : '卖出信号提醒'
    })
    
    const signalCounts = computed(() => {
      if (!props.signal) return {}
      return {
        buy: props.signal.buy_signals,
        sell: props.signal.sell_signals
      }
    })
    
    const closeDialog = () => {
      dialogVisible.value = false
    }
    
    return {
      dialogVisible,
      signalType,
      title,
      signalCounts,
      closeDialog
    }
  }
}
</script>

<style scoped>
.signal-alert-dialog :deep(.el-dialog__body) {
  padding: 30px;
}

.alert-content {
  text-align: center;
}

.alert-content.buy {
  --signal-color: #67c23a;
}

.alert-content.sell {
  --signal-color: #f56c6c;
}

.icon-wrapper {
  margin-bottom: 20px;
  color: var(--signal-color);
}

.signal-info h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
  color: #303133;
}

.signal-info .price {
  font-size: 18px;
  color: #606266;
  margin: 5px 0;
}

.signal-info .signal-count {
  font-size: 16px;
  color: var(--signal-color);
  font-weight: bold;
  margin: 10px 0;
}

.indicator-tags {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 15px;
}
</style>