# src/services/supabase_client.py
import logging
from supabase import create_client, Client
from typing import List, Dict, Any
from src.config import Config
from src.models.etf_price import ETFPrice

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        self.config = Config()
        self.client: Client = create_client(
            self.config.SUPABASE_URL,
            self.config.SUPABASE_KEY
        )
        self._create_table_if_not_exists()
    
    def _create_table_if_not_exists(self):
        """创建表（如果不存在）"""
        # 注意：实际表创建应该在Supabase控制台完成
        # 这里只是示例代码
        pass
    
    def insert_etf_price(self, etf_price: ETFPrice) -> bool:
        """插入ETF价格数据"""
        try:
            data = etf_price.to_dict()
            response = self.client.table(self.config.ETF_PRICES_TABLE).insert(data).execute()
            
            if response.data:
                logger.info(f"成功插入 {etf_price.symbol} 的价格数据")
                return True
            else:
                logger.error(f"插入 {etf_price.symbol} 数据失败")
                return False
                
        except Exception as e:
            logger.error(f"插入ETF价格数据时出错: {str(e)}")
            return False
    
    def batch_insert_etf_prices(self, etf_prices: List[ETFPrice]) -> bool:
        """批量插入ETF价格数据"""
        try:
            data = [price.to_dict() for price in etf_prices]
            response = self.client.table(self.config.ETF_PRICES_TABLE).insert(data).execute()
            
            if response.data:
                logger.info(f"成功批量插入 {len(etf_prices)} 条ETF价格数据")
                return True
            else:
                logger.error("批量插入ETF价格数据失败")
                return False
                
        except Exception as e:
            logger.error(f"批量插入ETF价格数据时出错: {str(e)}")
            return False
    
    def get_existing_price(self, symbol: str, date: str) -> bool:
        """检查某天的价格数据是否已存在"""
        try:
            response = (
                self.client.table(self.config.ETF_PRICES_TABLE)
                .select("*")
                .eq("symbol", symbol)
                .eq("date", date)
                .execute()
            )
            
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"检查价格数据是否存在时出错: {str(e)}")
            return False
    
    def get_etf_list(self) -> List[str]:
        """从数据库获取ETF列表"""
        try:
            response = self.client.table(self.config.ETF_LIST_TABLE)\
                                .select("symbol")\
                                .eq("is_active", True)\
                                .execute()
            
            if response.data:
                symbols = [item["symbol"] for item in response.data]
                logger.info(f"从数据库获取到 {len(symbols)} 个活跃ETF")
                return symbols
            else:
                logger.warning("数据库中没有活跃的ETF，使用默认列表")
                return self.config.DEFAULT_ETF_SYMBOLS
                
        except Exception as e:
            logger.error(f"获取ETF列表时出错: {str(e)}")
            return self.config.DEFAULT_ETF_SYMBOLS