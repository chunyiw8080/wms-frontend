from datetime import datetime
from config import SALT
import hashlib


def convert_date_to_chinese(date_str):
    # 将英文日期字符串解析为 datetime 对象
    date_obj = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")

    # 英文与中文的星期和月份映射
    week_map = {
        "Mon": "星期一", "Tue": "星期二", "Wed": "星期三",
        "Thu": "星期四", "Fri": "星期五", "Sat": "星期六", "Sun": "星期日"
    }
    month_map = {
        "Jan": "1", "Feb": "2", "Mar": "3", "Apr": "4",
        "May": "5", "Jun": "6", "Jul": "7", "Aug": "8",
        "Sep": "9", "Oct": "10", "Nov": "11", "Dec": "12"
    }

    # 获取中文星期和月份
    week_chinese = week_map[date_obj.strftime("%a")]
    month_chinese = month_map[date_obj.strftime("%b")]

    # 格式化为中文日期字符串
    chinese_date = f"{date_obj.year}-{month_chinese}-{date_obj.day} "
    # {week_chinese}
    return chinese_date


def get_keys_by_value(d, target_value):
    return [k for k, v in d.items() if v == target_value]


def hash_password(password: str) -> str:
    try:
        salted_passoword = password + SALT
        hashed_password = hashlib.sha256(salted_passoword.encode('utf-8')).hexdigest()
        return hashed_password
    except Exception as e:
        print(e)
