from sqlalchemy import Column, String, Float, Date, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class FinancialIndicator(BaseModel):
    """财务指标"""
    __tablename__ = 'stock_financials'
    
    id = Column(String(50), primary_key=True, index=True)
    stock_code = Column(String(10), ForeignKey('stock_basic.code'), nullable=False, index=True)
    report_date = Column(Date, nullable=False, index=True, comment='报告期')
    
    # 成长能力指标
    net_profit = Column(BigInteger, comment='净利润(元)')
    net_profit_growth = Column(Float, comment='净利润同比增长率(%)')
    non_net_profit = Column(BigInteger, comment='扣非净利润(元)')
    non_net_profit_growth = Column(Float, comment='扣非净利润同比增长率(%)')
    total_revenue = Column(BigInteger, comment='营业总收入(元)')
    total_revenue_growth = Column(Float, comment='营业总收入同比增长率(%)')
    
    # 每股指标
    eps = Column(Float, comment='基本每股收益(元)')
    bps = Column(Float, comment='每股净资产(元)')
    capital_reserve_per_share = Column(Float, comment='每股资本公积金(元)')
    undist_profit_per_share = Column(Float, comment='每股未分配利润(元)')
    ocfps = Column(Float, comment='每股经营现金流(元)')
    
    # 盈利能力指标
    net_profit_margin = Column(Float, comment='销售净利率(%)')
    gross_profit_margin = Column(Float, comment='销售毛利率(%)')
    roe = Column(Float, comment='净资产收益率(%)')
    roe_diluted = Column(Float, comment='净资产收益率-摊薄(%)')
    
    # 运营能力指标
    operating_cycle = Column(Float, comment='营业周期(天)')
    inventory_turnover = Column(Float, comment='存货周转率(次)')
    inventory_turnover_days = Column(Float, comment='存货周转天数(天)')
    receivable_turnover_days = Column(Float, comment='应收账款周转天数(天)')
    
    # 偿债能力指标
    current_ratio = Column(Float, comment='流动比率')
    quick_ratio = Column(Float, comment='速动比率')
    conservative_quick_ratio = Column(Float, comment='保守速动比率')
    equity_ratio = Column(Float, comment='产权比率')
    debt_ratio = Column(Float, comment='资产负债率(%)')
    
    # 关联关系
    stock = relationship("Stock", back_populates="financial_indicators")