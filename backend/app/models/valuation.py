from sqlalchemy import Column, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class StockValuation(BaseModel):
    """股票估值指标"""
    __tablename__ = 'stock_valuations'
    
    id = Column(String(50), primary_key=True, index=True)
    stock_code = Column(String(10), ForeignKey('stock_basic.code'), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True, comment='日期')
    
    # 估值指标
    pe_ttm = Column(Float, comment='市盈率(TTM)')
    pb = Column(Float, comment='市净率')
    ps_ttm = Column(Float, comment='市销率(TTM)')
    dividend_yield_ttm = Column(Float, comment='股息率TTM(%)')
    
    # 关联关系
    stock = relationship("Stock", back_populates="valuations") 