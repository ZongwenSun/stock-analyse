import re
from typing import Any, Union, Optional, Dict
from datetime import date

def convert_financial_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    转换财务数据，根据值的情况处理：
    1. 带"万"、"亿"的数字去掉单位转为浮点数
    2. 带百分号 % 的去掉 % 转为浮点数
    3. 其他尝试转为浮点数，失败则返回原始字符串
    """
    result = {}
    for key, value in data.items():
        if value is False or not value:
            result[key] = None
            continue
        if isinstance(value, (int, float)):
            result[key] = float(value)
            continue
        value_str = str(value).strip()
        if not value_str:
            result[key] = None
            continue
        if '万亿' in value_str:
            result[key] = int(round(float(value_str.replace('万亿', '')) * 1000000000000))
        elif '万' in value_str:
            result[key] = int(round(float(value_str.replace('万', '')) * 10000))
        elif '亿' in value_str:
            result[key] = int(round(float(value_str.replace('亿', '')) * 100000000))
        elif '%' in value_str:
            result[key] = float(value_str.replace('%', ''))
        else:
            try:
                result[key] = float(value_str)
            except ValueError:
                result[key] = value_str
    return result