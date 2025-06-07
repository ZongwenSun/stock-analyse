import logging
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from app.core.config import settings
from app.db.session import Base
from app.models.stock import Stock
from app.models.financial import FinancialIndicator
from app.models.valuation import StockValuation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    """初始化数据库"""
    try:
        # 创建数据库（如果不存在）
        if not database_exists(settings.DATABASE_URL):
            create_database(settings.DATABASE_URL)
            logger.info("数据库创建成功")
        
        # 创建表
        engine = create_engine(settings.DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise

if __name__ == "__main__":
    init_db() 