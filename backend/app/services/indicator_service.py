# 技术指标计算服务
import pandas as pd
import numpy as np

class IndicatorService:
    def __init__(self):
        pass
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> dict:
        """计算所有指标"""
        if df is None or len(df) < 30:
            return None
        
        result = {}
        
        # MACD
        result['macd'] = self.calculate_macd(df)
        
        # KDJ
        result['kdj'] = self.calculate_kdj(df)
        
        # RSI
        result['rsi'] = self.calculate_rsi(df)
        
        # 均线
        result['ma'] = self.calculate_ma(df)
        
        # 成交量
        result['volume'] = self.calculate_volume(df)
        
        # 布林带
        result['boll'] = self.calculate_boll(df)
        
        # 当前价格
        result['current_price'] = float(df['close'].iloc[-1])
        result['change_pct'] = float((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100)
        
        return result
    
    def calculate_macd(self, df: pd.DataFrame, fast=12, slow=26, signal=9) -> dict:
        """计算MACD指标"""
        close = df['close']
        
        # 计算EMA
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        
        # DIF和DEA
        dif = ema_fast - ema_slow
        dea = dif.ewm(span=signal, adjust=False).mean()
        macd = (dif - dea) * 2
        
        # 判断信号
        current_dif = dif.iloc[-1]
        current_dea = dea.iloc[-1]
        prev_dif = dif.iloc[-2]
        prev_dea = dea.iloc[-2]
        
        signal_type = "中性"
        if prev_dif <= prev_dea and current_dif > current_dea:
            signal_type = "金叉"
        elif prev_dif >= prev_dea and current_dif < current_dea:
            signal_type = "死叉"
        
        return {
            'dif': float(current_dif),
            'dea': float(current_dea),
            'macd': float(macd.iloc[-1]),
            'signal': signal_type
        }
    
    def calculate_kdj(self, df: pd.DataFrame, n=9) -> dict:
        """计算KDJ指标"""
        low_list = df['low'].rolling(window=n, min_periods=n).min()
        high_list = df['high'].rolling(window=n, min_periods=n).max()
        rsv = (df['close'] - low_list) / (high_list - low_list) * 100
        
        k = rsv.ewm(com=2, adjust=False).mean()
        d = k.ewm(com=2, adjust=False).mean()
        j = 3 * k - 2 * d
        
        current_k = k.iloc[-1]
        current_d = d.iloc[-1]
        prev_k = k.iloc[-2]
        prev_d = d.iloc[-2]
        
        signal_type = "中性"
        if prev_k <= prev_d and current_k > current_d and current_k < 20:
            signal_type = "金叉"
        elif prev_k >= prev_d and current_k < current_d and current_k > 80:
            signal_type = "死叉"
        
        return {
            'k': float(current_k),
            'd': float(current_d),
            'j': float(j.iloc[-1]),
            'signal': signal_type
        }
    
    def calculate_rsi(self, df: pd.DataFrame, period=14) -> dict:
        """计算RSI指标"""
        close = df['close']
        delta = close.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        signal_type = "中性"
        if current_rsi < 30:
            signal_type = "超卖"
        elif current_rsi > 70:
            signal_type = "超买"
        
        return {
            'value': float(current_rsi),
            'signal': signal_type
        }
    
    def calculate_ma(self, df: pd.DataFrame, short=5, long=20) -> dict:
        """计算均线信号"""
        close = df['close']
        
        ma_short = close.rolling(window=short).mean()
        ma_long = close.rolling(window=long).mean()
        
        current_short = ma_short.iloc[-1]
        current_long = ma_long.iloc[-1]
        prev_short = ma_short.iloc[-2]
        prev_long = ma_long.iloc[-2]
        
        signal_type = "中性"
        if prev_short <= prev_long and current_short > current_long:
            signal_type = "金叉"
        elif prev_short >= prev_long and current_short < current_long:
            signal_type = "死叉"
        
        return {
            'ma5': float(close.rolling(window=5).mean().iloc[-1]),
            'ma10': float(close.rolling(window=10).mean().iloc[-1]),
            'ma20': float(current_long),
            'signal': signal_type
        }
    
    def calculate_volume(self, df: pd.DataFrame) -> dict:
        """计算成交量信号"""
        volume = df['volume']
        volume_ma5 = volume.rolling(window=5).mean()
        
        current_volume = volume.iloc[-1]
        current_ma5 = volume_ma5.iloc[-1]
        
        signal_type = "中性"
        if current_volume > current_ma5 * 1.5:
            signal_type = "放量"
        elif current_volume < current_ma5 * 0.5:
            signal_type = "缩量"
        
        return {
            'current': float(current_volume),
            'ma5': float(current_ma5),
            'signal': signal_type
        }
    
    def calculate_boll(self, df: pd.DataFrame, period=20, std_dev=2) -> dict:
        """计算布林带信号"""
        close = df['close']
        
        middle = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()
        upper = middle + std_dev * std
        lower = middle - std_dev * std
        
        current_close = close.iloc[-1]
        current_upper = upper.iloc[-1]
        current_lower = lower.iloc[-1]
        prev_close = close.iloc[-2]
        
        signal_type = "中轨"
        if current_close <= current_lower:
            signal_type = "下轨"
        elif current_close >= current_upper:
            signal_type = "上轨"
        
        # 检测反弹/回落
        if prev_close <= current_lower and current_close > prev_close:
            signal_type = "下轨反弹"
        elif prev_close >= current_upper and current_close < prev_close:
            signal_type = "上轨回落"
        
        return {
            'upper': float(current_upper),
            'middle': float(middle.iloc[-1]),
            'lower': float(current_lower),
            'signal': signal_type
        }

indicator_service = IndicatorService()
