import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Backtest from '../views/Backtest.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { title: '实时监控' }
  },
  {
    path: '/backtest',
    name: 'Backtest',
    component: Backtest,
    meta: { title: '策略回测' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router