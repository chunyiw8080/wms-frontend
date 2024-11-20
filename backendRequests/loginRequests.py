import requests, json
from urllib3.exceptions import NewConnectionError

from config import URL

login_url = URL + '/users/login'


def login_request(username: str, password: str, session: requests.Session) -> bool:
    headers = {'Content-Type': 'application/json'}
    data = {
        'username': username,
        'password': password
    }
    try:
        response = session.post(login_url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False
