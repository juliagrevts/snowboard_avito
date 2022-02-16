from bs4 import BeautifulSoup
import requests


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0'
}
SEARCH_QUERY_URL = 'https://www.avito.ru/moskva/sport_i_otdyh/zimnie_vidy_sporta-ASgBAgICAUTKAtoK?bt=1&cd=1&q=сноуборд'


def get_avito_page_html(url, params=None, headers=None):
    try:
        result = requests.get(url, params=params, headers=headers)
        result.raise_for_status()
        return result.text
    except requests.RequestException as exception:
        print('Ошибка на сервере - {}'.format(exception))

def get_snowboard_page_link(max_pages=200):
    snowboards_links_list = []
    for page in range(1, max_pages):
        avito_page_html = get_avito_page_html(
            SEARCH_QUERY_URL,
            params={'p': page},
            headers=HEADERS
        )
        if not avito_page_html:
            continue
        soup = BeautifulSoup(avito_page_html, 'html.parser')
        snowboards_snippets_on_page = soup.find('div', class_='items-items-kAJAg').findAll('div', class_='iva-item-content-rejJg')
        for snowboard_snippet in snowboards_snippets_on_page:
            snowboard_page_link = snowboard_snippet.find('a', class_='link-link-MbQDP')['href']
            snowboards_links_list.append(snowboard_page_link)
            return snowboards_links_list
        
        # Check that the product pages on the web-site are over
        next_button_deactivated = soup.find('span', class_='pagination-item_readonly-_rHaf')
        if next_button_deactivated and 'След.' in next_button_deactivated.text:
            break
