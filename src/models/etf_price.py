# src/models/etf_price.py
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class ETFPrice:
    """ETF价格数据模型"""
    symbol: str
    date: str  # YYYY-MM-DD格式
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None
    adj_close: Optional[float] = None
    volume: Optional[int] = None
    after_hours_price: Optional[float] = None  # 盘后价格
    timestamp: Optional[datetime] = None
    
    def to_dict(self):
        """转换为字典格式"""
        data = asdict(self)
        if self.timestamp:
            data['timestamp'] = self.timestamp.isoformat()
        return data