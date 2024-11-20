import requests, json
from urllib3.exceptions import NewConnectionError

from config import URL

def fetch_inventory_data(session: requests.Session):
    headers = {'Content-Type': 'application/json'}
    url = URL + '/inventory/all'
    try:
        response = session.get(url, headers=headers)

        # 检查状态码是否为 200 成功
        if response.status_code == 200:
            return response.json()  # 假设返回 JSON 格式的列表
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"请求出现异常: {e}")
        return None

