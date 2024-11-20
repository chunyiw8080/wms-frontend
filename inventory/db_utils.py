from backendRequests.jsonRequests import get_request


def load_categories() -> list or None:
    try:
        items = get_request('http://127.0.0.1:5000/inventory/categories/get')
        if items['categories']:
            seen = set()
            unique_values = [item['categories'] for item in items['categories'] if
                             item['categories'] not in seen and not seen.add(item['categories'])]
            return unique_values
        else:
            return None
    except Exception as e:
        print(e)
