import asyncio
import logging
import akshare as ak
from datetime import datetime
import json
from app.utils.data_converter import convert_financial_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_financial_indicators(stock_code: str) -> list:
    """获取财务指标历史数据"""
    loop = asyncio.get_event_loop()
    df = await loop.run_in_executor(None, ak.stock_financial_abstract_ths, stock_code, "按报告期")
    if not df.empty:
        return df.to_dict(orient="records")
    return []

async def check_financial_format():
    """检查财务指标数据格式"""
    # 测试几个不同行业的股票
    test_stocks = [
        "600028", # 中国石化
    ]
    
    for stock_code in test_stocks:
        logger.info(f"\n检查股票 {stock_code} 的财务指标格式:")
        indicators_list = await get_financial_indicators(stock_code)
        
        if not indicators_list:
            logger.warning(f"无法获取股票 {stock_code} 的财务指标")
            continue
            
        # 打印第一期的数据格式
        if indicators_list:
            for indicator in indicators_list:
                # 原始数据
                logger.info("原始数据格式示例（第一期）:")
                logger.info(json.dumps(indicator, ensure_ascii=False, indent=2))
                
                # 转换后的数据
                converted_data = convert_financial_data(indicator)
                logger.info("\n转换后的数据格式:")
                logger.info(json.dumps(converted_data, ensure_ascii=False, indent=2))
                
                # 打印所有字段的类型
                logger.info("\n转换后的字段类型信息:")
                for key, value in converted_data.items():
                    logger.info(f"{key}: {type(value).__name__} = {value}")

async def main():
    await check_financial_format()

if __name__ == "__main__":
    asyncio.run(main()) 