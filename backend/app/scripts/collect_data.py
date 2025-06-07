import asyncio
import logging
import akshare as ak
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.stock import Stock
from app.models.financial import FinancialIndicator
from app.utils.data_converter import convert_financial_data
from typing import List, Dict, Any, Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_stock_list() -> list:
    """获取 A 股列表"""
    loop = asyncio.get_event_loop()
    a_stocks = await loop.run_in_executor(None, ak.stock_info_a_code_name)
    a_stocks["market"] = "A股"
    a_stocks = a_stocks[["code", "name", "market"]]
    return a_stocks.to_dict(orient="records")

async def get_stock_detail(stock_code: str) -> dict:
    """获取单只股票的基本信息"""
    loop = asyncio.get_event_loop()
    df = await loop.run_in_executor(None, ak.stock_individual_info_em, stock_code)
    info = {row["item"]: row["value"] for _, row in df.iterrows()}
    return {
        "code": info.get("股票代码"),
        "name": info.get("股票简称"),
        "industry": info.get("行业"),
        "market": "A股",
        "list_date": info.get("上市时间"),
    }

async def get_financial_indicators(stock_code: str) -> List[Dict[str, Any]]:
    """获取股票的历史财务指标"""
    try:
        # 获取股票信息以获取行业
        stock_info = await get_stock_detail(stock_code)
        industry = stock_info.get('industry', '')
        
        # 获取财务指标数据
        data = ak.stock_financial_abstract_ths(symbol=stock_code)
        if data is None or data.empty:
            logger.warning(f"股票 {stock_code} 没有财务指标数据")
            return []
            
        # 转换为字典列表
        records = data.to_dict('records')
        
        # 转换数据格式
        converted_records = []
        for record in records:
            converted_record = convert_financial_data(record)
            converted_record['报告期'] = record['报告期']  # 保持报告期不变
            converted_records.append(converted_record)
            
        return converted_records
    except Exception as e:
        logger.error(f"获取股票 {stock_code} 的财务指标时出错: {str(e)}")
        return []

async def collect_stock_list(db: Session):
    """收集股票列表数据"""
    logger.info("开始收集股票列表...")
    stocks = await get_stock_list()
    logger.info(f"获取到 {len(stocks)} 只股票")
    
    for stock_data in stocks:
        # 获取详细信息
        detail = await get_stock_detail(stock_data["code"])
        if not detail:
            logger.warning(f"无法获取股票 {stock_data['code']} 的详细信息")
            continue
            
        # 创建或更新股票记录
        stock = db.query(Stock).filter(Stock.code == detail["code"]).first()
        if not stock:
            # 处理上市日期
            listing_date = None
            if detail["list_date"]:
                try:
                    # 处理 YYYYMMDD 格式的日期
                    date_str = str(detail["list_date"])
                    if len(date_str) == 8:
                        listing_date = datetime.strptime(date_str, "%Y%m%d").date()
                    else:
                        logger.warning(f"股票 {detail['code']} 的上市日期格式不正确: {date_str}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"无法解析股票 {detail['code']} 的上市日期: {detail['list_date']}, 错误: {str(e)}")
            
            stock = Stock(
                code=detail["code"],
                name=detail["name"],
                industry=detail["industry"],
                market=detail["market"],
                listing_date=listing_date
            )
            db.add(stock)
            logger.info(f"添加新股票: {detail['code']} - {detail['name']} ({detail['industry']})")
        else:
            stock.name = detail["name"]
            stock.industry = detail["industry"]
            stock.market = detail["market"]
            if detail["list_date"]:
                try:
                    # 处理 YYYYMMDD 格式的日期
                    date_str = str(detail["list_date"])
                    if len(date_str) == 8:
                        stock.listing_date = datetime.strptime(date_str, "%Y%m%d").date()
                    else:
                        logger.warning(f"股票 {detail['code']} 的上市日期格式不正确: {date_str}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"无法解析股票 {detail['code']} 的上市日期: {detail['list_date']}, 错误: {str(e)}")
            logger.info(f"更新股票信息: {detail['code']} - {detail['name']} ({detail['industry']})")
    
    db.commit()
    logger.info(f"股票列表收集完成，共 {len(stocks)} 条记录")

async def process_stock_financial_indicators(db: Session, stock: Stock) -> None:
    """获取指定股票的财务指标并添加到数据库"""
    try:
        indicators_list = await get_financial_indicators(stock.code)
        if not indicators_list:
            logger.warning(f"无法获取股票 {stock.code} - {stock.name} 的财务指标")
            return
        logger.info(f"获取到股票 {stock.code} - {stock.name} 的 {len(indicators_list)} 期财务指标")
        for indicators in indicators_list:
            converted_data = convert_financial_data(indicators)
            report_date_str = converted_data.get('报告期')
            if not report_date_str:
                logger.warning(f"股票 {stock.code} - {stock.name} 某期财务指标缺少报告期，跳过该条记录: {converted_data}")
                continue
            try:
                report_date = datetime.strptime(report_date_str, "%Y-%m-%d").date()
            except ValueError:
                logger.warning(f"股票 {stock.code} - {stock.name} 的报告期格式不正确: {report_date_str}")
                continue
            financial = FinancialIndicator(
                id=f"{stock.code}_{report_date}",
                stock_code=stock.code,
                report_date=report_date,
                net_profit=converted_data.get('净利润'),
                net_profit_growth=converted_data.get('净利润同比增长率'),
                non_net_profit=converted_data.get('扣非净利润'),
                non_net_profit_growth=converted_data.get('扣非净利润同比增长率'),
                total_revenue=converted_data.get('营业总收入'),
                total_revenue_growth=converted_data.get('营业总收入同比增长率'),
                eps=converted_data.get('基本每股收益'),
                bps=converted_data.get('每股净资产'),
                capital_reserve_per_share=converted_data.get('每股资本公积金'),
                undist_profit_per_share=converted_data.get('每股未分配利润'),
                ocfps=converted_data.get('每股经营现金流'),
                net_profit_margin=converted_data.get('销售净利率'),
                gross_profit_margin=converted_data.get('销售毛利率'),
                roe=converted_data.get('净资产收益率'),
                roe_diluted=converted_data.get('净资产收益率-摊薄'),
                operating_cycle=converted_data.get('营业周期'),
                inventory_turnover=converted_data.get('存货周转率'),
                inventory_turnover_days=converted_data.get('存货周转天数'),
                receivable_turnover_days=converted_data.get('应收账款周转天数'),
                current_ratio=converted_data.get('流动比率'),
                quick_ratio=converted_data.get('速动比率'),
                conservative_quick_ratio=converted_data.get('保守速动比率'),
                equity_ratio=converted_data.get('产权比率'),
                debt_ratio=converted_data.get('资产负债率')
            )
            existing = db.query(FinancialIndicator).filter(FinancialIndicator.id == financial.id).first()
            if not existing:
                db.add(financial)
                logger.info(f"添加股票 {stock.code} - {stock.name} 的财务指标，报告期：{report_date}")
            else:
                logger.info(f"股票 {stock.code} - {stock.name} 的报告期 {report_date} 财务指标已存在，跳过")
        db.commit()
        logger.info(f"股票 {stock.code} - {stock.name} 的财务指标处理完成并提交")
    except Exception as e:
        logger.error(f"处理股票 {stock.code} - {stock.name} 时出错: {str(e)}")
        db.rollback()

async def collect_financial_indicators(db: Session):
    """收集财务指标数据"""
    logger.info("开始收集财务指标...")
    stocks = db.query(Stock).all()
    logger.info(f"开始处理 {len(stocks)} 只股票的财务指标")
    for stock in stocks:
        await process_stock_financial_indicators(db, stock)
    logger.info("财务指标收集完成")


async def collect_financial_indicators_by_code(stock_code: str):
    """收集指定股票的财务指标"""
    db = SessionLocal()
    try:
        stock = db.query(Stock).filter(Stock.code == stock_code).first()
        if not stock:
            logger.warning(f"股票 {stock_code} 不存在")
            return
        await process_stock_financial_indicators(db, stock)
    finally:
        db.close()

async def main():
    db = SessionLocal()
    try:
        missing_stocks = db.query(Stock).outerjoin(FinancialIndicator).filter(FinancialIndicator.stock_code == None).all()
        logger.info(f"找到 {len(missing_stocks)} 只没有财务指标的股票")
        for stock in missing_stocks:
            await process_stock_financial_indicators(db, stock)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main()) 