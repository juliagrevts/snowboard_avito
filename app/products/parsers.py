import requests

def get_avito_page_html(url):
    try:
        result = requests.get(url)
        result.raise_for_status()
        return result.text
    except requests.RequestException as exception:
        print('Ошибка на сервере - {}'.format(exception))
