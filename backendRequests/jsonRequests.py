import json

import requests

def get_request(url: str) -> json or str:
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # 如果返回状态码非 200-299，抛出 HTTPError
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error occurred: {e}"


def post_request(url: str, data: dict) -> json or str:
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error occurred: {e}"

def delete_request(url: str, id_list: list) -> json or str:
    headers = {
        "Content-Type": "application/json"
    }
    try:
        data = {"ids": id_list}  # 构造 JSON 数据
        response = requests.delete(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error occurred: {e}"