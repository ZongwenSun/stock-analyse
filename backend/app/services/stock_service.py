from typing import List, Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
import json
from datetime import datetime

class StockService:
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        
    def execute_sql(self, sql: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        执行 SQL 查询并返回 JSON 格式的结果
        
        Args:
            sql: SQL 查询语句
            params: 查询参数
            
        Returns:
            List[Dict[str, Any]]: 查询结果列表，每个元素是一个字典
        """
        try:
            # 执行 SQL 查询
            result = self.db.execute(text(sql), params or {})
            
            # 将结果转换为字典列表
            rows = []
            for row in result:
                # 处理每个字段的值
                row_dict = {}
                for key, value in row._mapping.items():
                    # 处理日期时间类型
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    row_dict[key] = value
                rows.append(row_dict)
                
            return rows
            
        except Exception as e:
            raise Exception(f"执行 SQL 查询时出错: {str(e)}")
            
    def __del__(self):
        """确保关闭数据库连接"""
        if self.db:
            self.db.close() 