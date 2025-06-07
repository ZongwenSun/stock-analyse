from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.stock_service import StockService
from datetime import date

router = APIRouter()

class SQLQuery(BaseModel):
    """SQL 查询请求模型"""
    sql: str
    params: Optional[Dict[str, Any]] = None

class StockInfo(BaseModel):
    """股票基本信息模型"""
    code: str
    name: str
    industry: Optional[str] = None
    market: Optional[str] = None
    listing_date: Optional[date] = None

class FinancialIndicator(BaseModel):
    """财务指标模型"""
    # 基本信息
    report_date: date
    
    # 成长能力指标
    net_profit: Optional[int] = None
    net_profit_growth: Optional[float] = None
    non_net_profit: Optional[int] = None
    non_net_profit_growth: Optional[float] = None
    total_revenue: Optional[int] = None
    total_revenue_growth: Optional[float] = None
    
    # 每股指标
    eps: Optional[float] = None
    bps: Optional[float] = None
    capital_reserve_per_share: Optional[float] = None
    undist_profit_per_share: Optional[float] = None
    ocfps: Optional[float] = None
    
    # 盈利能力指标
    net_profit_margin: Optional[float] = None
    gross_profit_margin: Optional[float] = None
    roe: Optional[float] = None
    roe_diluted: Optional[float] = None
    
    # 运营能力指标
    operating_cycle: Optional[float] = None
    inventory_turnover: Optional[float] = None
    inventory_turnover_days: Optional[float] = None
    receivable_turnover_days: Optional[float] = None
    
    # 偿债能力指标
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    conservative_quick_ratio: Optional[float] = None
    equity_ratio: Optional[float] = None
    debt_ratio: Optional[float] = None

class StockValuation(BaseModel):
    """股票估值指标模型"""
    date: date
    pe_ttm: Optional[float] = None
    pb: Optional[float] = None
    ps_ttm: Optional[float] = None
    dividend_yield_ttm: Optional[float] = None

@router.get("/{stock_code}/basic", response_model=StockInfo)
async def get_stock_info(stock_code: str):
    """
    获取股票基本信息
    
    Args:
        stock_code: 股票代码
        
    Returns:
        StockInfo: 股票基本信息
        
    Raises:
        HTTPException: 当股票不存在或查询出错时抛出
    """
    try:
        service = StockService()
        sql = """
        SELECT 
            code,
            name,
            industry,
            market,
            listing_date
        FROM stock_basic 
        WHERE code = :code
        """
        result = service.execute_sql(sql, {"code": stock_code})
        
        if not result:
            raise HTTPException(status_code=404, detail=f"股票 {stock_code} 不存在")
            
        return result[0]
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        service.__del__()

@router.get("/{stock_code}/financials", response_model=List[FinancialIndicator])
async def get_stock_financials(
    stock_code: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: Optional[int] = 10
):
    """
    获取股票历史财务指标
    
    Args:
        stock_code: 股票代码
        start_date: 开始日期（可选）
        end_date: 结束日期（可选）
        limit: 返回记录数量限制（可选，默认10条）
        
    Returns:
        List[FinancialIndicator]: 财务指标列表
        
    Raises:
        HTTPException: 当查询出错时抛出
    """
    try:
        service = StockService()
        
        # 构建查询条件
        conditions = ["stock_code = :code"]
        params = {"code": stock_code}
        
        if start_date:
            conditions.append("report_date >= :start_date")
            params["start_date"] = start_date
        if end_date:
            conditions.append("report_date <= :end_date")
            params["end_date"] = end_date
            
        # 构建 SQL
        sql = f"""
        SELECT 
            report_date,
            -- 成长能力指标
            net_profit,
            net_profit_growth,
            non_net_profit,
            non_net_profit_growth,
            total_revenue,
            total_revenue_growth,
            -- 每股指标
            eps,
            bps,
            capital_reserve_per_share,
            undist_profit_per_share,
            ocfps,
            -- 盈利能力指标
            net_profit_margin,
            gross_profit_margin,
            roe,
            roe_diluted,
            -- 运营能力指标
            operating_cycle,
            inventory_turnover,
            inventory_turnover_days,
            receivable_turnover_days,
            -- 偿债能力指标
            current_ratio,
            quick_ratio,
            conservative_quick_ratio,
            equity_ratio,
            debt_ratio
        FROM stock_financials 
        WHERE {' AND '.join(conditions)}
        ORDER BY report_date DESC
        LIMIT :limit
        """
        params["limit"] = limit
        
        result = service.execute_sql(sql, params)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        service.__del__()

@router.get("/{stock_code}/valuations", response_model=List[StockValuation])
async def get_stock_valuations(
    stock_code: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: Optional[int] = 10
):
    """
    获取股票历史估值指标
    
    Args:
        stock_code: 股票代码
        start_date: 开始日期（可选）
        end_date: 结束日期（可选）
        limit: 返回记录数量限制（可选，默认10条）
        
    Returns:
        List[StockValuation]: 估值指标列表
        
    Raises:
        HTTPException: 当查询出错时抛出
    """
    try:
        service = StockService()
        
        # 构建查询条件
        conditions = ["stock_code = :code"]
        params = {"code": stock_code}
        
        if start_date:
            conditions.append("date >= :start_date")
            params["start_date"] = start_date
        if end_date:
            conditions.append("date <= :end_date")
            params["end_date"] = end_date
            
        # 构建 SQL
        sql = f"""
        SELECT 
            date,
            pe_ttm,
            pb,
            ps_ttm,
            dividend_yield_ttm
        FROM stock_valuations 
        WHERE {' AND '.join(conditions)}
        ORDER BY date DESC
        LIMIT :limit
        """
        params["limit"] = limit
        
        result = service.execute_sql(sql, params)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        service.__del__()

@router.post("/execute-sql", response_model=List[Dict[str, Any]])
async def execute_sql(query: SQLQuery):
    """
    执行 SQL 查询并返回结果
    
    Args:
        query: SQL 查询请求，包含 SQL 语句和可选的参数
        
    Returns:
        List[Dict[str, Any]]: 查询结果列表
        
    Raises:
        HTTPException: 当查询执行出错时抛出
    """
    try:
        service = StockService()
        result = service.execute_sql(query.sql)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        service.__del__() 