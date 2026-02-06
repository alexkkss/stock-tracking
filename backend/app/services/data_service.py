# 数据获取服务
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

class DataService:
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 60  # 缓存60秒
    
    def get_stock_data(self, stock_code: str, days: int = 100) -> pd.DataFrame:
        """获取股票历史数据"""
        cache_key = f"{stock_code}_{days}"
        
        # 检查缓存
        if cache_key in self.cache:
            if datetime.now() - self.cache_time[cache_key] < timedelta(seconds=self.cache_duration):
                return self.cache[cache_key]
        
        try:
            # 使用akshare获取数据
            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period="daily",
                start_date=(datetime.now() - timedelta(days=days)).strftime("%Y%m%d"),
                end_date=datetime.now().strftime("%Y%m%d"),
                adjust="qfq"  # 前复权
            )
            
            if df.empty:
                return None
            
            # 重命名列
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount'
            })
            
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)
            
            # 更新缓存
            self.cache[cache_key] = df
            self.cache_time[cache_key] = datetime.now()
            
            return df
            
        except Exception as e:
            print(f"获取股票数据失败: {e}")
            return None
    
    def get_realtime_quote(self, stock_code: str) -> dict:
        """获取实时行情"""
        try:
            # 获取实时行情
            df = ak.stock_zh_a_spot_em()
            stock_row = df[df['代码'] == stock_code]
            
            if stock_row.empty:
                return None
            
            return {
                'code': stock_code,
                'name': stock_row['名称'].values[0],
                'price': float(stock_row['最新价'].values[0]),
                'change': float(stock_row['涨跌幅'].values[0]),
                'volume': float(stock_row['成交量'].values[0]),
                'amount': float(stock_row['成交额'].values[0]),
                'high': float(stock_row['最高'].values[0]),
                'low': float(stock_row['最低'].values[0]),
                'open': float(stock_row['今开'].values[0]),
                'pre_close': float(stock_row['昨收'].values[0]),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"获取实时行情失败: {e}")
            return None

data_service = DataService()
