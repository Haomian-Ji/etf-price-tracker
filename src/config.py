# src/config.py
import os
from dotenv import load_dotenv

# 在GitHub Actions中，环境变量已经设置
# 但在本地开发时仍需要加载.env文件
if os.path.exists('.env'):
    load_dotenv()

class Config:
    # Supabase配置
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    
    # 股票API配置（备用）
    ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")
    FINNHUB_KEY = os.getenv("FINNHUB_KEY", "")
    
    # 数据库表名
    ETF_PRICES_TABLE = "etf_prices"
    ETF_LIST_TABLE = "etf_list"
    
    # 要跟踪的ETF列表（默认值）
    DEFAULT_ETF_SYMBOLS = [
        "SPY", "QQQ", "DIA", "IWM", "VTI",
        "VOO", "IVV", "GLD", "TLT", "EFA", "EEM"
    ]