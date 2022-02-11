from bs4 import BeautifulSoup
import requests

from config import HEADERS

def get_avito_page_html(url, number_of_page):
    params = {'p': number_of_page}
    try:
        result = requests.get(url, params=params, headers=HEADERS)
        result.raise_for_status()
        return result.text
    except requests.RequestException as exception:
        print('Ошибка на сервере - {}'.format(exception))

def get_snowboard_page_link():
    max_pages = 1000
    for page in range(1, max_pages):
        avito_page_html = get_avito_page_html(
            'https://www.avito.ru/moskva/sport_i_otdyh/zimnie_vidy_sporta-ASgBAgICAUTKAtoK?bt=1&cd=1&q=сноуборд',
            page
        )
        if avito_page_html:
            soup = BeautifulSoup(avito_page_html, 'html.parser')
            snowboards_snippets_on_page = soup.find('div', class_='items-items-kAJAg').findAll('div', class_='iva-item-content-rejJg')
            for snowboard_snippet in snowboards_snippets_on_page:
                snowboard_page_link = snowboard_snippet.find('a', class_='link-link-MbQDP')['href']
                print(snowboard_page_link)
        next_button_deactivated = soup.find('span', class_='pagination-item_readonly-_rHaf')
        if next_button_deactivated and 'След.' in next_button_deactivated.text:
            break
