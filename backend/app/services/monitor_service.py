# 监控引擎服务
from datetime import datetime
from typing import Dict, List, Callable
from app.services.data_service import data_service
from app.services.indicator_service import indicator_service
from app.database import SessionLocal, IndicatorHistory, SignalAlert

class MonitorService:
    def __init__(self):
        self.current_stock = "600489"
        self.stock_name = "中金黄金"
        self.is_running = False
        self.callbacks: List[Callable] = []
        self.last_signal = None  # 避免重复提示
    
    def set_stock(self, code: str, name: str = ""):
        """设置监控股票"""
        self.current_stock = code
        self.stock_name = name
        self.last_signal = None
        print(f"切换监控股票: {code} {name}")
    
    def register_callback(self, callback: Callable):
        """注册信号回调函数"""
        self.callbacks.append(callback)
    
    def check_signals(self) -> dict:
        """检查指标信号"""
        try:
            # 获取数据
            df = data_service.get_stock_data(self.current_stock)
            if df is None:
                return None
            
            # 计算指标
            indicators = indicator_service.calculate_all_indicators(df)
            if indicators is None:
                return None
            
            # 统计信号
            buy_count = 0
            sell_count = 0
            
            # MACD
            if indicators['macd']['signal'] == "金叉":
                buy_count += 1
            elif indicators['macd']['signal'] == "死叉":
                sell_count += 1
            
            # KDJ
            if indicators['kdj']['signal'] == "金叉":
                buy_count += 1
            elif indicators['kdj']['signal'] == "死叉":
                sell_count += 1
            
            # RSI
            if indicators['rsi']['signal'] == "超卖":
                buy_count += 1
            elif indicators['rsi']['signal'] == "超买":
                sell_count += 1
            
            # MA
            if indicators['ma']['signal'] == "金叉":
                buy_count += 1
            elif indicators['ma']['signal'] == "死叉":
                sell_count += 1
            
            # Volume
            if indicators['volume']['signal'] == "放量":
                buy_count += 1
            elif indicators['volume']['signal'] == "缩量":
                sell_count += 1
            
            # Boll
            if indicators['boll']['signal'] == "下轨反弹":
                buy_count += 1
            elif indicators['boll']['signal'] == "上轨回落":
                sell_count += 1
            
            # 确定最终信号
            final_signal = "HOLD"
            signal_count = 0
            
            if buy_count >= 4:
                final_signal = "BUY"
                signal_count = buy_count
            elif sell_count >= 4:
                final_signal = "SELL"
                signal_count = sell_count
            
            result = {
                'stock_code': self.current_stock,
                'stock_name': self.stock_name,
                'timestamp': datetime.now().isoformat(),
                'price': indicators['current_price'],
                'change_pct': indicators['change_pct'],
                'indicators': indicators,
                'buy_signals': buy_count,
                'sell_signals': sell_count,
                'final_signal': final_signal,
                'signal_count': signal_count
            }
            
            # 保存到数据库
            self._save_to_db(result)
            
            # 触发信号提醒
            if final_signal in ["BUY", "SELL"] and final_signal != self.last_signal:
                self._trigger_alert(result)
                self.last_signal = final_signal
            
            return result
            
        except Exception as e:
            print(f"检查信号失败: {e}")
            return None
    
    def _save_to_db(self, result: dict):
        """保存到数据库"""
        try:
            db = SessionLocal()
            history = IndicatorHistory(
                stock_code=result['stock_code'],
                macd_signal=result['indicators']['macd']['signal'],
                kdj_signal=result['indicators']['kdj']['signal'],
                rsi_value=result['indicators']['rsi']['value'],
                rsi_signal=result['indicators']['rsi']['signal'],
                ma_signal=result['indicators']['ma']['signal'],
                volume_signal=result['indicators']['volume']['signal'],
                boll_signal=result['indicators']['boll']['signal'],
                buy_signals=result['buy_signals'],
                sell_signals=result['sell_signals'],
                final_signal=result['final_signal']
            )
            db.add(history)
            db.commit()
            db.close()
        except Exception as e:
            print(f"保存历史记录失败: {e}")
    
    def _trigger_alert(self, result: dict):
        """触发信号提醒"""
        try:
            # 保存提醒记录
            db = SessionLocal()
            alert = SignalAlert(
                stock_code=result['stock_code'],
                signal_type=result['final_signal'],
                signal_count=result['signal_count'],
                price=result['price'],
                details=f"{result['buy_signals']}个买入信号, {result['sell_signals']}个卖出信号"
            )
            db.add(alert)
            db.commit()
            db.close()
            
            # 调用回调函数
            for callback in self.callbacks:
                try:
                    callback(result)
                except Exception as e:
                    print(f"回调函数执行失败: {e}")
                    
        except Exception as e:
            print(f"触发提醒失败: {e}")
    
    def get_recent_alerts(self, limit: int = 20) -> list:
        """获取最近的信号提醒"""
        try:
            db = SessionLocal()
            alerts = db.query(SignalAlert).filter(
                SignalAlert.stock_code == self.current_stock
            ).order_by(SignalAlert.timestamp.desc()).limit(limit).all()
            
            result = []
            for alert in alerts:
                result.append({
                    'id': alert.id,
                    'signal_type': alert.signal_type,
                    'signal_count': alert.signal_count,
                    'price': alert.price,
                    'timestamp': alert.timestamp.isoformat(),
                    'details': alert.details
                })
            
            db.close()
            return result
        except Exception as e:
            print(f"获取提醒历史失败: {e}")
            return []

monitor_service = MonitorService()
