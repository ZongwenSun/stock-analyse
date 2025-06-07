import logging
import akshare as ak
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_stock_dividend(stock_code: str):
    """查询股票的历史分红数据"""
    try:
        # 获取分红数据
        df = ak.stock_history_dividend_detail(symbol=stock_code, indicator="分红")
        if df is None or df.empty:
            logger.warning(f"股票 {stock_code} 没有分红数据")
            return
            
        # 按年份分组统计
        df['year'] = pd.to_datetime(df['除权除息日']).dt.year
        yearly_stats = df.groupby('year').agg({
            '分红金额': 'sum',
            '分红金额': 'count'
        }).rename(columns={'分红金额': '分红次数'})
        
        # 计算累计分红
        total_dividend = df['分红金额'].sum()
        
        # 打印详细信息
        logger.info(f"\n股票 {stock_code} 的分红历史：")
        logger.info(f"累计分红次数：{len(df)}次")
        logger.info(f"累计分红金额：{total_dividend:.2f}元")
        logger.info("\n年度分红统计：")
        for year, row in yearly_stats.iterrows():
            logger.info(f"{year}年：分红{row['分红次数']}次，金额{row['分红金额']:.2f}元")
            
        # 打印最近5次分红详情
        logger.info("\n最近5次分红详情：")
        recent_dividends = df.sort_values('除权除息日', ascending=False).head(5)
        for _, row in recent_dividends.iterrows():
            logger.info(f"除权除息日：{row['除权除息日']}，分红金额：{row['分红金额']:.2f}元")
            
    except Exception as e:
        logger.error(f"查询股票 {stock_code} 的分红数据时出错: {str(e)}")

if __name__ == "__main__":
    check_stock_dividend("000001") 