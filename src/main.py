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

from src.services.stock_api import StockDataAPI, AlphaVantageAPI
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
        
        # 初始化配置
        config = Config()
        
        # 检查关键配置
        if not config.SUPABASE_URL or not config.SUPABASE_KEY:
            logger.error("❌ 关键配置缺失，无法继续执行")
            logger.error(f"SUPABASE_URL: {'已设置' if config.SUPABASE_URL else '未设置'}")
            logger.error(f"SUPABASE_KEY: {'已设置' if config.SUPABASE_KEY else '未设置'}")
            sys.exit(1)
        
        # 初始化数据源
        stock_api = StockDataAPI()
        alpha_vantage_api = None
        
        # 如果有Alpha Vantage密钥，初始化备用API
        if config.ALPHA_VANTAGE_KEY:
            alpha_vantage_api = AlphaVantageAPI(config.ALPHA_VANTAGE_KEY)
        else:
            logger.info("未配置Alpha Vantage API密钥，仅使用yfinance")
        
        # 初始化Supabase客户端
        supabase_client = SupabaseClient()
        
        # 获取ETF列表 - 这是之前缺失的关键步骤！
        try:
            etf_symbols = supabase_client.get_etf_list()
            logger.info(f"从数据库获取到 {len(etf_symbols)} 个ETF需要跟踪")
            logger.info(f"ETF列表: {', '.join(etf_symbols)}")
        except Exception as e:
            logger.error(f"获取ETF列表失败: {str(e)}")
            logger.info(f"使用默认ETF列表")
            etf_symbols = config.DEFAULT_ETF_SYMBOLS
        
        if not etf_symbols:
            logger.error("没有需要跟踪的ETF，任务结束")
            sys.exit(0)
        
        # 获取价格数据
        successful_count = 0
        failed_symbols = []
        
        for symbol in etf_symbols:
            try:
                logger.info(f"正在处理: {symbol}")
                
                # 首先尝试 yfinance
                etf_price = stock_api.get_etf_price(symbol)
                
                # 如果 yfinance 失败，尝试 Alpha Vantage（如果可用）
                if not etf_price and alpha_vantage_api:
                    logger.info(f"yfinance 失败，尝试 Alpha Vantage 获取 {symbol}")
                    etf_price = alpha_vantage_api.get_etf_price(symbol)
                
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
                    logger.warning(f"⚠️  {symbol} 数据获取失败（所有数据源）")
                    
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