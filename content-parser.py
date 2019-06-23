# -*- coding: utf-8 -*-
#%% run
import pandas as pd
import csv
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent
import requests
import time
import re
import json
import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['tripadvisor']
collection = db['restaurants']

domain = 'https://www.tripadvisor.com'
ua = UserAgent()
header = {'User-Agent': str(ua.chrome)}

df = pd.read_csv('./data/url_parser.csv')
total_restaurants = len(df)
debug = True
if debug:
    limit = 10
else:
    limit = None

data = {}
data['restaurants'] = []

for index, u in enumerate(df['url'][:limit]):
    restaurant_id = df['restaurant_id'][index]
    restaurant_name = df['restaurant_name'][index]

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome('./chromedriver', chrome_options=options)
    driver.get(u)
    driver.maximize_window()

    # r = requests.get(u, headers=header)
    # soup = BeautifulSoup(r.text, 'html.parser')
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    next_page = '//div[@class="prw_rup prw_common_responsive_pagination"]/div/a[@class="nav next taLnk ui_button primary"]'
    last_page = soup.find('a', {
        "class": "pageNum last taLnk"
    }).get('data-page-number')
    page_down = "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;"
    page_list = range(int(last_page))
    read_more = '//div[@class="prw_rup prw_reviews_text_summary_hsx"]/div/p/span[@class="taLnk ulBlueLinks"]'

    actions = ActionChains(driver)

    id = 0
    review = {}
    review['reviews'] = []
    for p in page_list:
        print('process = {}/{} page {}/{}'.format(index + 1, total_restaurants,
                                                  p + 1, last_page))

        review_blocks = soup.find_all('div', {"class": "reviewSelector"})

        more_button = driver.find_element_by_xpath(read_more)
        actions.move_to_element(more_button).click()

        for element in review_blocks:
            id += 1
            name = element.find('div', {"class": "info_text"}).find('div').text
            rating = element.select(
                'span[class*="ui_bubble_rating bubble_"]')[0].get('class')[1]
            rating = int(re.sub('[^0-9,]', "", rating).replace(',', '')) / 10
            date = element.find('span', {"class": "ratingDate"}).get('title')
            title = element.find('span', {"class": "noQuotes"}).text

            detail = element.find('p', {"class": "partial_entry"}).text
            review['reviews'].append({
                # 'index': int(id),
                'name': name,
                'rating': rating,
                'date': date,
                'title': title,
                'detail': detail
            })

        try:
            # driver.execute_script(page_down)
            # time.sleep(5)
            element = driver.find_element_by_xpath(next_page)
            actions.move_to_element(element).click()
            time.sleep(8)
        except Exception as e:
            print(e)

    data['restaurants'].append({
        # 'id': int(restaurant_id),
        'name': restaurant_name,
        'reviews': review['reviews']
    })

with open('data/content_parser.json', 'a') as outfile:
    json.dump(data, outfile)

# result = collection.insert_many(data['restaurants'])

driver.quit()
