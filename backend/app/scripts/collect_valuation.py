import asyncio
import logging
import akshare as ak
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.stock import Stock
from app.models.valuation import StockValuation
import pandas as pd
from sqlalchemy import not_
import time
from requests.exceptions import RequestException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_stock_valuation(stock_code: str, max_retries: int = 3) -> list:
    """获取股票的估值指标，返回每月第一天的数据"""
    for retry in range(max_retries):
        try:
            # 获取估值指标数据
            df = ak.stock_a_indicator_lg(symbol=stock_code)
            if df is None or df.empty:
                logger.warning(f"股票 {stock_code} 没有估值指标数据")
                return None
                
            # 将日期列转换为日期类型
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            
            # 按月份分组，取每月第一天的数据
            df['year_month'] = df['trade_date'].dt.to_period('M')
            monthly_data = df.groupby('year_month').first().reset_index()
            
            # 转换回日期格式
            monthly_data['trade_date'] = monthly_data['trade_date'].dt.date
            
            logger.info(f"股票 {stock_code} 的月度估值指标数据: {monthly_data}")
            
            # 转换为字典列表
            result = []
            for _, row in monthly_data.iterrows():
                result.append({
                    'date': row['trade_date'],
                    'pe_ttm': row['pe_ttm'],
                    'pb': row['pb'],
                    'ps_ttm': row['ps_ttm'],
                    'dividend_yield_ttm': row['dv_ttm']  # 股息率
                })
            return result
            
        except (RequestException, Exception) as e:
            if retry < max_retries - 1:
                wait_time = (retry + 1) * 5  # 递增等待时间：5秒、10秒、15秒
                logger.warning(f"获取股票 {stock_code} 的估值指标失败，{wait_time}秒后重试 ({retry + 1}/{max_retries}): {str(e)}")
                time.sleep(wait_time)
            else:
                logger.error(f"获取股票 {stock_code} 的估值指标失败，已达到最大重试次数: {str(e)}")
                return None

async def process_stock_valuation(db: Session, stock: Stock) -> None:
    """处理单个股票的估值指标"""
    try:
        # 获取估值指标
        valuation_data_list = await get_stock_valuation(stock.code)
        if not valuation_data_list:
            return
            
        for valuation_data in valuation_data_list:
            # 创建估值指标记录
            valuation = StockValuation(
                id=f"{stock.code}_{valuation_data['date']}",
                stock_code=stock.code,
                date=valuation_data['date'],
                pe_ttm=valuation_data['pe_ttm'],
                pb=valuation_data['pb'],
                ps_ttm=valuation_data['ps_ttm'],
                dividend_yield_ttm=valuation_data['dividend_yield_ttm']
            )
            
            # 检查是否已存在
            existing = db.query(StockValuation).filter(
                StockValuation.id == valuation.id
            ).first()
            
            if not existing:
                db.add(valuation)
                logger.info(f"添加股票 {stock.code} - {stock.name} 的估值指标，日期：{valuation_data['date']}")
            else:
                logger.info(f"股票 {stock.code} - {stock.name} 的估值指标已存在，日期：{valuation_data['date']}")
                
        db.commit()
        
    except Exception as e:
        logger.error(f"处理股票 {stock.code} - {stock.name} 的估值指标时出错: {str(e)}")
        db.rollback()

async def collect_valuations():
    """收集所有股票的估值指标"""
    db = SessionLocal()
    try:
        # 查找还没有估值数据的股票
        stocks_without_valuation = db.query(Stock).filter(
            not_(Stock.code.in_(
                db.query(StockValuation.stock_code).distinct()
            ))
        ).all()
        
        logger.info(f"找到 {len(stocks_without_valuation)} 只没有估值数据的股票")
        
        for stock in stocks_without_valuation:
            logger.info(f"处理股票 {stock.code} - {stock.name}")
            await process_stock_valuation(db, stock)
            # 每处理完一只股票，等待1秒，避免请求过于频繁
            await asyncio.sleep(1)
            
        logger.info("估值指标收集完成")
    finally:
        db.close()

async def collect_valuation_by_code(stock_code: str):
    """收集指定股票的估值指标"""
    db = SessionLocal()
    try:
        stock = db.query(Stock).filter(Stock.code == stock_code).first()
        if not stock:
            logger.warning(f"股票 {stock_code} 不存在")
            return
        await process_stock_valuation(db, stock)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(collect_valuations())