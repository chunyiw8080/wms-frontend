from datetime import datetime

import jwt
import pytz
from config import TOKEN_SECRET_KEY


def decode_token(token: str) -> dict:
    """
    解码 JWT Token 并返回载荷部分

    :param token: JWT Token 字符串
    :param secret_key: 用于验证 JWT 的密钥，如果是公钥/私钥签名的话使用公钥/私钥
    :return: 解码后的载荷（字典形式）
    """
    try:
        # 通过 PyJWT 解码 Token，验证签名并提取载荷 , options={"verify_signature": False}
        payload = jwt.decode(token, TOKEN_SECRET_KEY, algorithms=["HS256"])
        china_timezone = pytz.timezone('Asia/Shanghai')
        current_time = datetime.now(china_timezone)
        exp_time = datetime.fromtimestamp(payload['exp'], china_timezone)
        iat_time = datetime.fromtimestamp(payload['iat'], china_timezone)

        # print(f"Current time: {current_time}")
        # print(f"Token issued at: {iat_time}")
        # print(f"Token expires at: {exp_time}")

        return payload
    except jwt.ExpiredSignatureError:
        print("Token 已过期")
    except jwt.InvalidTokenError:
        print("无效的 Token")
    return {}


def get_privilege(token: str) -> str:
    payload = jwt.decode(token, TOKEN_SECRET_KEY, algorithms=["HS256"])
    return payload.get('permissions')
