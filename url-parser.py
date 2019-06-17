# -*- coding: utf-8 -*-
#%% run
from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import time
import csv
import re

options = webdriver.ChromeOptions()
options.add_argument('headless')
domain = 'https://www.tripadvisor.com'
target_url = 'https://www.tripadvisor.com/Restaurants-g297715-Surabaya_East_Java_Java.html'
driver = webdriver.Chrome('./chromedriver', chrome_options=options)
driver.get(target_url)
driver.maximize_window()

soup = BeautifulSoup(driver.page_source, 'html.parser')

# scrape page
next_page = '//div[@class="unified pagination js_pageLinks"]/a[@class="nav next rndBtn ui_button primary taLnk"]'
pagination_div = soup.select('div.unified.pagination.js_pageLinks > div > a')
page_down = "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;"
last_a = None
for last_a in pagination_div:
    pass
if last_a:
    last_page = last_a

page_list = range(int(last_page.get('data-page-number')))
print("Total number of page: {}".format(len(page_list)))

with open('./data/url_parser.csv', 'a') as csvfile:
    fieldnames = [
        'restaurant_id', 'restaurant_name', 'rating', 'n_comment', 'rank',
        'url'
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    index = 0

    for p in page_list:
        print('the number of page = {0}/{1}'.format(p + 1, len(page_list)))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        restaurant_blocks = soup.select(
            'div[class*="listing rebrand listingIndex-"]')
        for element in restaurant_blocks:
            index += 1
            restaurant_name = element.find('a', {
                "class": "property_title"
            }).text
            restaurant_name = restaurant_name.strip('\n').replace('\"', '')

            url = domain + element.find('a', {
                "class": "property_title"
            }).get('href')

            rating = None
            if len(element.select(
                    'span[class*="ui_bubble_rating bubble_"]')) > 0:
                rating = element.select(
                    'span[class*="ui_bubble_rating bubble_"]')[0].get(
                        'alt').replace(' of 5 bubbles', '')

            try:
                n_comment = element.find('span', {"class": "reviewCount"}).text
                n_comment = re.sub('[^0-9,]', "", n_comment).replace(',', '')
            except AttributeError:
                n_comment = None

            try:
                rank = element.find('div', {
                    "class": "popIndex rebrand popIndexDefault"
                }).text.strip('\n').strip('\"')
            except AttributeError:
                rank = None

            writer.writerow({
                'restaurant_id': index,
                'restaurant_name': restaurant_name,
                'rating': rating,
                'n_comment': n_comment,
                'rank': rank,
                'url': url
            })
        try:
            driver.execute_script(page_down)
            time.sleep(5)
            driver.find_element_by_xpath(next_page).click()
            time.sleep(8)
        except:
            print('in the end')

driver.quit()