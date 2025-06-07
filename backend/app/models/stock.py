from sqlalchemy import Column, String, Date, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Stock(BaseModel):
    """股票基本信息"""
    __tablename__ = 'stock_basic'
    
    code = Column(String(10), primary_key=True, index=True, comment='股票代码')
    name = Column(String(50), nullable=False, comment='股票名称')
    industry = Column(String(50), comment='所属行业')
    market = Column(String(20), comment='市场类型')
    listing_date = Column(Date, comment='上市日期')
    
    # 关联关系
    valuations = relationship("StockValuation", back_populates="stock") 