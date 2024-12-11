import json
from utils.worker import Worker
import requests


class APIClient:
    jwt_token = None  # 用于保存 JWT Token

    @staticmethod
    def set_jwt_token(token: str):
        """设置 JWT Token"""
        APIClient.jwt_token = token

    @staticmethod
    def get_headers():
        """生成请求头，包含 JWT Token"""
        headers = {"Content-Type": "application/json"}
        if APIClient.jwt_token:
            headers["Authorization"] = f"Bearer {APIClient.jwt_token}"
        return headers

    @Worker.run_in_thread_with_result
    def get_request(url: str, is_stream=False) -> json or str:

        try:
            headers = APIClient.get_headers()
            response = requests.get(url, headers=headers, timeout=30, stream=is_stream)
            response.raise_for_status()  # 如果返回状态码非 200-299，抛出 HTTPError
            if is_stream:
                return response.content
            else:
                return response.json()
        except requests.exceptions.RequestException as e:
            return f"Error occurred: {e}"

    @Worker.run_in_thread_with_result
    def post_request(url: str, data: dict) -> json or str:
        try:
            headers = APIClient.get_headers()
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return f"Error occurred: {e}"

    @Worker.run_in_thread_with_result
    def delete_request(url: str, id_list: list) -> json or str:
        try:
            headers = APIClient.get_headers()
            data = {"ids": id_list}  # 构造 JSON 数据
            response = requests.delete(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return f"Error occurred: {e}"
