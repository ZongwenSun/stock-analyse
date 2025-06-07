import pytest
from app.services.stock_service import StockService
from app.db.session import SessionLocal
from app.models.stock import Stock
from datetime import datetime

@pytest.fixture
def db():
    """创建测试数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def stock_service(db):
    """创建 StockService 实例"""
    return StockService(db)

def test_execute_sql_basic(stock_service):
    """测试基本的 SQL 查询"""
    # 准备测试数据
    sql = "SELECT * FROM stocks LIMIT 5"
    result = stock_service.execute_sql(sql)
    
    # 验证结果
    assert isinstance(result, list)
    if result:  # 如果数据库中有数据
        assert isinstance(result[0], dict)
        assert 'code' in result[0]
        assert 'name' in result[0]

def test_execute_sql_with_join(stock_service):
    """测试带 JOIN 的 SQL 查询"""
    sql = """
    SELECT s.code, s.name, v.pe_ttm, v.pb, v.date
    FROM stocks s
    LEFT JOIN stock_valuations v ON s.code = v.stock_code
    WHERE s.code = '000001'
    ORDER BY v.date DESC
    LIMIT 1
    """
    result = stock_service.execute_sql(sql)
    
    # 验证结果
    assert isinstance(result, list)
    if result:  # 如果数据库中有数据
        assert isinstance(result[0], dict)
        assert 'code' in result[0]
        assert 'name' in result[0]
        assert 'pe_ttm' in result[0]
        assert 'pb' in result[0]
        assert 'date' in result[0]

def test_execute_sql_with_aggregation(stock_service):
    """测试带聚合函数的 SQL 查询"""
    sql = """
    SELECT 
        stock_code,
        COUNT(*) as valuation_count,
        AVG(pe_ttm) as avg_pe,
        AVG(pb) as avg_pb
    FROM stock_valuations
    GROUP BY stock_code
    LIMIT 5
    """
    result = stock_service.execute_sql(sql)
    
    # 验证结果
    assert isinstance(result, list)
    if result:  # 如果数据库中有数据
        assert isinstance(result[0], dict)
        assert 'stock_code' in result[0]
        assert 'valuation_count' in result[0]
        assert 'avg_pe' in result[0]
        assert 'avg_pb' in result[0]

def test_execute_sql_error_handling(stock_service):
    """测试错误处理"""
    # 测试无效的 SQL
    with pytest.raises(Exception):
        stock_service.execute_sql("INVALID SQL")

def test_execute_sql_date_handling(stock_service):
    """测试日期处理"""
    sql = """
    SELECT date, pe_ttm
    FROM stock_valuations
    WHERE stock_code = '000001'
    ORDER BY date DESC
    LIMIT 1
    """
    result = stock_service.execute_sql(sql)
    
    # 验证结果
    assert isinstance(result, list)
    if result:  # 如果数据库中有数据
        assert isinstance(result[0], dict)
        assert 'date' in result[0]
        # 验证日期是否被正确转换为 ISO 格式字符串
        assert isinstance(result[0]['date'], str)
        assert 'T' in result[0]['date']  # ISO 格式包含 'T' 