from datetime import datetime, timedelta
from lib2to3.pgen2 import driver
import locale
import platform
import random
import time
import sys

from selenium import webdriver
from selenium.common.exceptions import (SessionNotCreatedException,
    NoSuchElementException, WebDriverException)
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


def get_snowboard_pages_links(
    url=SEARCH_QUERY_URL, max_pages=101, filename: str = 'snowboards_links.txt'
):
    """This function launches the browser, that navigating through the pages of the web-site,
    collects snowboards links and writes them to the file
    """
    driver = launch_browser()
    links_set = set()
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            links_set.add(line)
    for page in range(1, max_pages):
        driver.get(url.replace('&p=1', f'&p={page}'))
        snowboard_snippets_on_page = driver.find_elements(By.CLASS_NAME, 'iva-item-content-rejJg')
        for snowboard_snippet in snowboard_snippets_on_page:
            try:
                snowboard_page_link = snowboard_snippet.find_element(
                    By.CLASS_NAME, 'link-link-MbQDP'
                ).get_attribute('href')
                if not snowboard_page_link[:-1] in links_set:
                    with open(filename, 'a', encoding='utf-8') as f:
                        f.write(snowboard_page_link + '\n')
                time.sleep(random.randint(5, 15)) # to avoid being blocked by Avito website
            except NoSuchElementException:
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


def get_html_element(driver, element_name: str):
    try:
        element = driver.find_element(By.CLASS_NAME, element_name) 
    except NoSuchElementException:
        element = None
    if element:
        element = element.text
    return element


def get_photo_links(driver):
    photo_links = []
    try:
        photo_links_list = driver.find_elements(
            By.CLASS_NAME, 'images-preview-previewImageWrapper-JwvC5'
        )
        if photo_links_list:
            search_forward_button = driver.find_element(
                By.CLASS_NAME, 'image-frame-controlButton-2fg1E'
            )
            for i in range(len(photo_links_list)):
                try:
                    search_forward_button.click()
                    photo_link = driver.find_element(
                        By.CLASS_NAME, 'image-frame-wrapper-28gKD'
                    ).get_attribute('data-url')
                    photo_links.append(photo_link)
                except NoSuchElementException:
                    photo_links.append(None)
        else:
            photo_link = driver.find_element(
                By.CLASS_NAME, 'image-frame-wrapper-28gKD'
            ).get_attribute('data-url')
            photo_links.append(photo_link)
    except NoSuchElementException:
        photo_links.append(None)
    
    return photo_links


def parse_snowboard(driver, snowboard_link):
    driver.get(snowboard_link)
    snowboard = {}

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
        element = get_html_element(driver, element_name)
        if element and element_name =='style-item-metadata-bzKjw':
            element = parse_placement_date(element)
        if element and element_name == 'js-item-price':
            element = element.replace('\xa0', '')
        if element and element_name == 'style-item-description-text-SzN56':
            element = element.replace('\xa0', ' ')
        beautiful_name = element_name_to_snowboard_feature[element_name]
        snowboard[beautiful_name] = element
    
    snowboard['photos_links_list'] = get_photo_links(driver)
               
    return snowboard


def save_all_snowboards(filename: str = 'snowboards_links.txt'):
    driver = launch_browser()
    with open(filename, 'r', encoding='utf-8') as f:
        for snowboard_link in f:
            try:
                snowboard = parse_snowboard(driver, snowboard_link)
                if not snowboard:
                    time.sleep(random.randint(5, 15)) 
                    continue
                if snowboard['product_name'] and snowboard['ad_placement_date'] and snowboard['price']:
                    save_snowboard(driver, snowboard)
                    time.sleep(random.randint(5, 15)) 
                else:
                    time.sleep(random.randint(5, 15)) 
                    continue
            except WebDriverException as driver_exception:
                print(f'Парсинг элементов сноуборда {snowboard_link} упал '
                'из-за {driver_exception}, иду дальше')
                continue 
            
    driver.close()


def save_snowboard(driver, snowboard):
    snowboards_exists = Snowboard.query.filter(Snowboard.url == driver.current_url).count()
    if not snowboards_exists:
        new_snowboard = Snowboard(
            product_name=snowboard['product_name'],
            ad_placement_date=snowboard['ad_placement_date'],
            price=snowboard['price'],
            url=driver.current_url,
            address=snowboard['address'],
            ad_text=snowboard['ad_text']
        )
        db.session.add(new_snowboard)
        db.session.commit()
        for photo_link in snowboard['photos_links_list']:
            photo_link_exists = SnowboardPhotoLink.query.filter(
                SnowboardPhotoLink.photo_link == photo_link
            ).count()
            if not photo_link_exists:
                new_photo_link = SnowboardPhotoLink(
                    photo_link=photo_link,
                    snowboard_id=new_snowboard.id
                )
                db.session.add(new_photo_link)
                db.session.commit()
