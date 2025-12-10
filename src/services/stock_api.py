# src/services/stock_api.py
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, Any
from src.models.etf_price import ETFPrice

logger = logging.getLogger(__name__)

class StockDataAPI:
    """股票数据API服务（使用yfinance）"""
    
    def __init__(self):
        self.yahoo_finance = yf
        
    def get_etf_price(self, symbol: str) -> Optional[ETFPrice]:
        """获取ETF的最新价格数据（包括盘后价格）"""
        try:
            # 获取股票ticker
            ticker = self.yahoo_finance.Ticker(symbol)
            
            # 获取历史数据（最近1天）
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)  # 多获取几天以防周末
            
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                logger.warning(f"未找到 {symbol} 的历史数据")
                return None
            
            # 获取最新一天的数据
            latest_data = hist.iloc[-1]
            
            # 获取当前盘后价格
            info = ticker.info
            
            # 创建ETF价格对象
            etf_price = ETFPrice(
                symbol=symbol,
                date=latest_data.name.strftime('%Y-%m-%d'),  # 交易日
                open_price=float(latest_data['Open']),
                high_price=float(latest_data['High']),
                low_price=float(latest_data['Low']),
                close_price=float(latest_data['Close']),
                adj_close=float(latest_data['Close']),  # yfinance中Adj Close可能相同
                volume=int(latest_data['Volume']),
                after_hours_price=info.get('postMarketPrice'),
                timestamp=datetime.now()
            )
            
            logger.info(f"成功获取 {symbol} 的价格数据")
            return etf_price
            
        except Exception as e:
            logger.error(f"获取 {symbol} 价格数据时出错: {str(e)}")
            return None
    
    def get_multiple_etf_prices(self, symbols: list) -> Dict[str, Optional[ETFPrice]]:
        """批量获取多个ETF的价格数据"""
        results = {}
        
        for symbol in symbols:
            price_data = self.get_etf_price(symbol)
            results[symbol] = price_data
            
        return results

class AlphaVantageAPI:
    """备用API：Alpha Vantage"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
    
    def get_quote_endpoint(self, symbol: str) -> Optional[Dict]:
        """获取最新报价"""
        import requests
        
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if "Global Quote" in data:
                return data["Global Quote"]
            else:
                logger.error(f"Alpha Vantage API错误: {data}")
                return None
                
        except Exception as e:
            logger.error(f"调用Alpha Vantage API时出错: {str(e)}")
            return None
        


# 在 stock_api.py 中添加以下类
import requests

class AlphaVantageAPI:
    """Alpha Vantage API 作为备用数据源"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        
    def get_etf_price(self, symbol: str) -> Optional[ETFPrice]:
        """通过Alpha Vantage获取ETF价格"""
        if not self.api_key:
            logger.warning("Alpha Vantage API密钥未配置")
            return None
            
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": self.api_key,
            "outputsize": "compact"
        }
        
        try:
            logger.info(f"通过Alpha Vantage获取 {symbol} 数据")
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if "Time Series (Daily)" not in data:
                logger.error(f"Alpha Vantage返回错误: {data.get('Note', 'Unknown error')}")
                return None
            
            # 获取最新的交易日数据
            time_series = data["Time Series (Daily)"]
            latest_date = sorted(time_series.keys(), reverse=True)[0]
            daily_data = time_series[latest_date]
            
            etf_price = ETFPrice(
                symbol=symbol,
                date=latest_date,
                open_price=float(daily_data["1. open"]),
                high_price=float(daily_data["2. high"]),
                low_price=float(daily_data["3. low"]),
                close_price=float(daily_data["4. close"]),
                adj_close=float(daily_data["4. close"]),
                volume=int(daily_data["5. volume"]),
                after_hours_price=float(daily_data["4. close"]),  # Alpha Vantage不提供盘后价
                timestamp=datetime.now()
            )
            
            logger.info(f"通过Alpha Vantage成功获取 {symbol} 数据")
            return etf_price
            
        except Exception as e:
            logger.error(f"Alpha Vantage API错误: {str(e)}")
            return None