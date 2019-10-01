#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 13:38:26 2019

@author: weetee
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import re
import time
from bs4 import BeautifulSoup
import os
import pickle
from tqdm import tqdm
import logging

logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', \
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
logger = logging.getLogger('__file__')

def save_as_pickle(filename, data):
    completeName = os.path.join("./data/",\
                                filename)
    with open(completeName, 'wb') as output:
        pickle.dump(data, output)
        
def crawl_google_reviews(search_query="changi+city+point", num_reviews=100):
    logger.info("Initialzing webdriver...")
    driver = webdriver.Chrome()
    
    driver.get("https://www.google.com/search?q=" + search_query)
    element = driver.find_elements_by_xpath('/html/body/div[7]/div[3]/div[10]/div[1]/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[1]/div[2]/div[2]/div[2]/div/div/span[2]/span/a')
    element[0].click()
    time.sleep(3)
    
    logger.info("Crawling...")
    error_count = 0
    all_reviews = WebDriverWait(driver, 7).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.gws-localreviews__google-review')))
    while len(all_reviews) < num_reviews:
        logger.info("%d/%d crawled." % (len(all_reviews), num_reviews))
        driver.execute_script('arguments[0].scrollIntoView(true);', all_reviews[-1])
        try:
            WebDriverWait(driver, 7, 0.25).until_not(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class$="activityIndicator"]')))
        except Exception as e:
            print(e)
            error_count += 1
            if error_count == 3:
                break
        
        all_reviews = driver.find_elements_by_css_selector('div.gws-localreviews__google-review')
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.close()
    logger.info("Finished crawling!")
    
    reviews = soup.find_all("div", class_=re.compile('WMbnJf.+'))
    logger.info("Extracting %d reviews..." % len(reviews))
    reviews_list = []
    for review in tqdm(reviews, total=len(reviews)):
        comment = review.find_all("span", class_="review-full-text")
        star = review.find_all("span", class_="fTKmHE99XE4__star fTKmHE99XE4__star-s")[0]["aria-label"]
        star = float(re.findall("Rated \d\.*\d*", star)[0][-3:])
        if len(comment) != 0:
            comment = comment[0].text
        else: 
            comment = review.find_all("span", tabindex=0)[0].text
        reviews_list.append((comment, star))
    
    save_as_pickle("reviews.pkl", reviews_list)
    with open("./data/google_reviews_%s.txt" % search_query.replace("+", "_"), "w", encoding="utf8") as f:
        for review, star in tqdm(reviews_list, total=len(reviews)):
            f.write("\"" + review + "\"" + " %s" % str(star) + "\n")
    logger.info("Done and saved!")
    
    return reviews_list

if __name__ == "__main__":
    reviews_list = crawl_google_reviews(search_query="changi+city+point", num_reviews=100)