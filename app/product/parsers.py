from datetime import datetime, timedelta
import locale
import platform
import random
import time
import sys

from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By

from app.db import db
from app.product.models import Snowboard, SnowboardPhotoLink


SEARCH_QUERY_URL = 'https://www.avito.ru/moskva/sport_i_otdyh/zimnie_vidy_sporta-ASgBAgICAUTKAtoK?bt=1&cd=1&p=1&q=сноуборд'


if platform.system() == 'Windows':
    locale.setlocale(locale.LC_ALL, 'russian')
else:
    locale.setlocale(locale.LC_TIME, 'ru_RU')


def launch_browser():
    try:
        driver = webdriver.Safari()
        return driver
    except SessionNotCreatedException as session_exception:
        print('Не удалось создать сессию')
        sys.exit()


def get_snowboard_pages_links(url, max_pages=101):
    """This function launches the browser, that navigating through the pages of the web-site,
    collects snowboards links and writes them to the file
    """
    driver = launch_browser()
    for page in range(1, max_pages):
        driver.get(url.replace('&p=1', f'&p={page}'))
        snowboard_snippets_on_page = driver.find_elements(By.CLASS_NAME, 'iva-item-content-rejJg')
        for snowboard_snippet in snowboard_snippets_on_page:
            try:
                snowboard_page_link = snowboard_snippet.find_element(By.CLASS_NAME, 'link-link-MbQDP').get_attribute('href')
                with open('snowboards_links.txt', 'a', encoding='utf-8') as f:
                    f.write(snowboard_page_link + '\n')
                time.sleep(random.randint(5, 15))
            except NoSuchElementException as element_exception:
                print('Ошибка при запуске драйвера или сборе ссылок')
                continue
    driver.quit()
 

def parse_placement_date(ad_placement_date):
    """This function brings the dates to a single format and 
    converts them from a string to datetime
    """
    today = datetime.now()
    yesterday = datetime.now() - timedelta(days=1)
    try:
        if 'сегодня' in ad_placement_date:
            ad_placement_date = ad_placement_date.replace('сегодня', today.strftime('%d %B %Y'))
            return datetime.strptime(ad_placement_date, '%d %B %Y в %H:%M')
        elif 'вчера' in ad_placement_date:
            ad_placement_date = ad_placement_date.replace('вчера', yesterday.strftime('%d %B %Y'))
            return datetime.strptime(ad_placement_date, '%d %B %Y в %H:%M')
        else:
            return datetime.strptime(ad_placement_date, '%d %B в %H:%M').replace(year=today.year)
    except ValueError:
        return today


def get_html_element_with_exception(driver, element_name: str):
    try:
        element = driver.find_element(By.CLASS_NAME, element_name) 
    except NoSuchElementException as element_exception:
        element = None
    if element:
        element = element.text
    return element


def get_photo_links_with_exception(driver, snowboard: list):
    try:
        photo_links_list = driver.find_elements(By.CLASS_NAME, 'images-preview-previewImageWrapper-JwvC5')
        if photo_links_list:
            search_forward_button = driver.find_element(By.CLASS_NAME, 'image-frame-controlButton-2fg1E')
            for i in range(len(photo_links_list)):
                try:
                    search_forward_button.click()
                    photo_link = driver.find_element(By.CLASS_NAME, 'image-frame-wrapper-28gKD').get_attribute('data-url')
                    snowboard.append(photo_link)
                except NoSuchElementException as element_exception:
                    snowboard.append(None)
        else:
            photo_link = driver.find_element(By.CLASS_NAME, 'image-frame-wrapper-28gKD').get_attribute('data-url')
            snowboard.append(photo_link)
    except NoSuchElementException as element_exception:
        snowboard.append(None)


def parse_html_elements(driver, snowboard_link):
    driver.get(snowboard_link)
    snowboard = {'photos_links_list': []}

    elements_names = [
        'title-info-title-text', 'style-item-metadata-bzKjw', 'js-item-price',
        'style-item-address__string-3Ct0s', 'style-item-description-text-SzN56'
    ]

    element_name_to_snowboard_feature = {
        'title-info-title-text': 'product_name',
        'style-item-metadata-bzKjw': 'ad_placement_date',
        'js-item-price': 'price',
        'style-item-address__string-3Ct0s': 'address',
        'style-item-description-text-SzN56': 'ad_text'
    }

    for element_name in elements_names:
        element = get_html_element_with_exception(driver, element_name)
        if element and element_name =='style-item-metadata-bzKjw':
            element = parse_placement_date(element)
        if element and (element_name == 'js-item-price' or element_name == 'style-item-description-text-SzN56'):
            element = element.replace('\xa0', '')
        beautiful_name = element_name_to_snowboard_feature[element_name]
        snowboard[beautiful_name] = element
    
    get_photo_links_with_exception(driver, snowboard['photos_links_list'])
               
    return snowboard


def save_product():
    driver = launch_browser()
    with open('snowboards_links.txt', 'r', encoding='utf-8') as f:
        for snowboard_link in f:
            try:
                snowboard = parse_html_elements(driver, snowboard_link)
                if not snowboard:
                    time.sleep(random.randint(5, 15)) 
                    continue
                if snowboard['product_name'] and snowboard['ad_placement_date'] and snowboard['price']:
                    new_snowboard_id = save_snowboard(
                        snowboard['product_name'],
                        snowboard['ad_placement_date'],
                        snowboard['price'],
                        driver.current_url,
                        snowboard['address'],
                        snowboard['ad_text']
                    )
                    for photo_link in snowboard['photos_links_list']:
                        save_photo_links(photo_link, new_snowboard_id)
                    time.sleep(random.randint(5, 15)) 
                else:
                    time.sleep(random.randint(5, 15)) 
                    continue
            except WebDriverException as driver_exception:
                print(f'Парсинг элементов сноуборда {snowboard_link} упал из-за {driver_exception}, иду дальше')
                continue 
            
    driver.close()


def save_snowboard(product_name, ad_placement_date, price, url=None, address=None, ad_text=None, user_id=None):
    snowboards_exists = Snowboard.query.filter(
        Snowboard.product_name == product_name, 
        Snowboard.price == price,
        Snowboard.ad_text == ad_text,
        Snowboard.user_id == user_id
    ).count()
    if not snowboards_exists:
        new_snowboard = Snowboard(
            product_name=product_name,
            ad_placement_date=ad_placement_date,
            price=price,
            url=url,
            address=address,
            ad_text=ad_text,
            user_id=user_id
        )
        db.session.add(new_snowboard)
        db.session.commit()
        return new_snowboard.id


def save_photo_links(photo_link, snowboard_id):
    photo_link_exists = SnowboardPhotoLink.query.filter(SnowboardPhotoLink.photo_link == photo_link).count()
    if not photo_link_exists:
        new_photo_link = SnowboardPhotoLink(photo_link=photo_link, snowboard_id=snowboard_id)
        db.session.add(new_photo_link)
        db.session.commit()
