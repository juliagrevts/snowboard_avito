from datetime import datetime, timedelta
import locale
import platform

from bs4 import BeautifulSoup
import requests


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0'
}
SEARCH_QUERY_URL = 'https://www.avito.ru/moskva/sport_i_otdyh/zimnie_vidy_sporta-ASgBAgICAUTKAtoK?bt=1&cd=1&q=сноуборд'


if platform.system() == 'Windows':
    locale.setlocale(locale.LC_ALL, 'russian')
else:
    locale.setlocale(locale.LC_TIME, 'ru_RU')


def get_page_html(url, params=None, headers=None):
    try:
        result = requests.get(url, params=params, headers=headers)
        result.raise_for_status()
        return result.text
    except requests.RequestException as exception:
        print('Ошибка на сервере - {}'.format(exception))


def get_snowboard_page_link(max_pages=200):
    snowboards_links_list = []
    for page in range(1, max_pages):
        avito_page_html = get_page_html(
            SEARCH_QUERY_URL,
            params={'p': page},
            headers=HEADERS
        )
        if not avito_page_html:
            continue
        soup = BeautifulSoup(avito_page_html, 'html.parser')
        snowboards_snippets_on_page = soup.find('div', class_='items-items-kAJAg').findAll('div', class_='iva-item-content-rejJg')
        for snowboard_snippet in snowboards_snippets_on_page:
            snowboard_page_link = ''.join(['https://www.avito.ru', snowboard_snippet.find('a', class_='link-link-MbQDP')['href']])
            snowboards_links_list.append(snowboard_page_link)
            return snowboards_links_list

        # Check that the product pages on the web-site are over
        next_button_deactivated = soup.find('span', class_='pagination-item_readonly-_rHaf')
        if next_button_deactivated and 'След.' in next_button_deactivated.text:
            break


def parse_placement_date(ad_placement_date):
    """This function brings the dates to a single format and 
    converts them from a string to datetime
    """
    today = datetime.now()
    yesterday = datetime.now() - timedelta(days=1)
    try:
        if 'сегодня' in ad_placement_date:
            ad_placement_date = ad_placement_date.replace('сегодня', today.strftime('%d %B %Y'))
            return datetime.strptime(ad_placement_date, '%d %B Y в %H:%M')
        elif 'вчера' in ad_placement_date:
            ad_placement_date = ad_placement_date.replace('вчера', yesterday.strftime('%d %B %Y'))
            return datetime.strptime(ad_placement_date, '%d %B Y в %H:%M')
        else:
            return datetime.strptime(ad_placement_date, '%d %B в %H:%M').replace(year=today.year)
    except ValueError:
        return today


def get_snowboard_page_html():
    snowboards_links_list = get_snowboard_page_link()
    for snowboard_link in snowboards_links_list:
        snowboard_page_html = get_page_html(snowboard_link)
        if not snowboard_page_html:
            continue
        soup = BeautifulSoup(snowboard_page_html, 'html.parser')
        product_name = soup.find('span', class_='title-info-title-text').text
        ad_number = soup.find('div', class_='item-view-search-info-redesign').find('span').text
        ad_placement_date = soup.find('div', class_='title-info-metadata-item-redesign').text.strip()
        ad_placement_date = parse_placement_date(ad_placement_date)
        photos_links_list = []
        photo_links = soup.findAll('div', class_='gallery-img-frame')
        for photo_link in photo_links:
            photos_links_list.append(photo_link['data-url'])
        address = soup.find('span', class_='item-address__string').text.strip()
        price = soup.find('span', class_='price-value-main').text.strip()
        ad_text = soup.find('div', class_='item-description-text').decode_contents()
        pass
