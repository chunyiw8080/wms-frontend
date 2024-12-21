from backendRequests.jsonRequests import APIClient
from config import URL
from utils.worker import Worker
from utils.app_logger import get_logger

error_logger = get_logger(logger_name='error_logger', log_file='error.log')

def load_categories() -> list or None:
    try:
        url = URL + '/inventory/categories/get'
        items = Worker.unpack_thread_queue(APIClient.get_request, url)
        # items = APIClient.get_request(url)
        if items.get('success') is True:
            seen = set()
            unique_values = [item['categories'] for item in items['categories'] if
                             item['categories'] not in seen and not seen.add(item['categories'])]
            return unique_values
        else:
            return None
    except Exception as e:
        error_logger.error(f'db_utils.load_categories: {e}')


def load_providers() -> list or None or str:
    url = URL + '/providers/all'
    try:

        items = Worker.unpack_thread_queue(APIClient.get_request, url)
        if items['success'] is True:
            providers = items['data']
            data = []
            for provider in providers:
                data.append(provider.get('provider_name'))

            return data
        else:
            return None
    except Exception as e:
        error_logger.error(f'db_utils.load_providers: {e}')

def load_projects() -> list or None or str:
    url = URL + '/project/all'
    try:

        items = Worker.unpack_thread_queue(APIClient.get_request, url)
        if items['success'] is True:
            projects = items['data']
            data = []
            for project in projects:
                if project.get('project_name') != 'null':
                    data.append(project.get('project_name'))

            return data
        else:
            return None
    except Exception as e:
        error_logger.error(f'db_utils.load_projects: {e}')