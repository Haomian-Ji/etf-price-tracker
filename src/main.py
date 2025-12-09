# src/main.py
#!/usr/bin/env python3
"""
ETF价格跟踪器 - GitHub Actions版本
每天自动获取美股ETF盘后价格并保存到Supabase
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# 添加到路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.services.stock_api import StockDataAPI
from src.services.supabase_client import SupabaseClient
from src.config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('etf_tracker.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """主函数"""
    try:
        # 加载环境变量
        load_dotenv()
        
        logger.info("=== ETF价格跟踪器开始执行 ===")
        logger.info(f"执行时间: {datetime.now()}")
        
        # 初始化配置和客户端
        config = Config()
        stock_api = StockDataAPI()
        supabase_client = SupabaseClient()
        
        # 获取ETF列表
        etf_symbols = supabase_client.get_etf_list()
        logger.info(f"需要跟踪的ETF数量: {len(etf_symbols)}")
        logger.info(f"ETF列表: {', '.join(etf_symbols)}")
        
        # 获取价格数据
        successful_count = 0
        failed_symbols = []
        
        for symbol in etf_symbols:
            try:
                logger.info(f"正在处理: {symbol}")
                
                # 获取ETF价格数据
                etf_price = stock_api.get_etf_price(symbol)
                
                if etf_price:
                    # 检查是否已存在
                    if not supabase_client.get_existing_price(symbol, etf_price.date):
                        # 插入数据库
                        if supabase_client.insert_etf_price(etf_price):
                            successful_count += 1
                            logger.info(f"✓ {symbol} 数据保存成功")
                        else:
                            failed_symbols.append(symbol)
                            logger.error(f"✗ {symbol} 数据保存失败")
                    else:
                        logger.info(f"⏭️ {symbol} 数据已存在，跳过")
                else:
                    failed_symbols.append(symbol)
                    logger.warning(f"⚠️  {symbol} 数据获取失败")
                    
            except Exception as e:
                failed_symbols.append(symbol)
                logger.error(f"处理 {symbol} 时出错: {str(e)}")
                continue
        
        # 输出执行结果
        logger.info("=== 执行结果汇总 ===")
        logger.info(f"成功处理: {successful_count}/{len(etf_symbols)}")
        logger.info(f"失败数量: {len(failed_symbols)}")
        
        if failed_symbols:
            logger.warning(f"失败的ETF: {', '.join(failed_symbols)}")
        
        # 在GitHub Actions中，如果失败数超过阈值则任务失败
        if len(failed_symbols) > len(etf_symbols) * 0.5:  # 超过50%失败
            logger.error("失败率过高，任务标记为失败")
            sys.exit(1)
            
        logger.info("=== ETF价格跟踪器执行完成 ===")
        
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()