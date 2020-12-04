#%%
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import datetime
import random
from dateutil.parser import parse

user_agent_list = [
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
]

initial_urls =  {'trading_view' : 'https://www.tradingview.com/symbols/',
                 'investing' : 'https://www.investing.com/equities/',
                  'wsj' : 'https://www.wsj.com/market-data/quotes/MY/',
                  'bursamktplace' : 'https://www.bursamarketplace.com/mkt/themarket/stock/',
                  'reuters' : 'https://www.reuters.com/companies/'}

stocks_dict =  {'AIRASIA' : ['MYX-AIRASIA', 'airasia-bhd', '5099', 'AIRA', 'AIRA.KL'],
                'GENM' : ['MYX-GENM', 'genting-malaysia-bhd', '4715', 'GENM', 'GENM.KL'],
                'NESTLE' : ['MYX-NESTLE', 'nestle-(malaysia)-bhd', '4707', 'NESM', 'NESM.KL'], 
                'GLOVE' : ['MYX-TOPGLOV', 'top-glove-corporation-bhd', '7113', 'TPGC',  'TPGC.KL']
                }

reuters_recommendation_class = 'TextLabel__text-label___3oCVw TextLabel__gray___1V4fk TextLabel__regular___2X0ym RecommendationBar-mean-info-2GEKb'
investing_monthly = """//*[@id="timePeriodsWidget"]/li[8]/a"""
investing_buy_number = 'maBuy'
investing_sell_number = 'maSell'
trading_view_monthly = '//*[@id="technicals-root"]/div/div/div[1]/div/div/div[1]/div/div/div[8]'
investing_monthly = '//*[@id="timePeriodsWidget"]/li[8]'

def get_driver(DRIVER_PATH, user_agent_list):
    user_agent = random.choice(user_agent_list)
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')                                                                                                                        
    # options.add_argument('--headless')
    options.add_argument("--disable-infobars")
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-extensions")
    options.add_argument("--incognito")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])         
    options.add_argument('--disable-dev-shm-usage')
    try: 
        driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options)
    except: 
        driver = webdriver.Chrome(DRIVER_PATH)   
    return driver

def open_website(driver, key, stock):
    if key == 'trading_view': 
        url = initial_urls[key] + stocks_dict[stock][0] + "/technicals"
    elif key == 'investing': 
        url = initial_urls[key] + stocks_dict[stock][1] + "-technical"
    elif key == 'wsj': 
        url = initial_urls[key] + stocks_dict[stock][2] + "/research-ratings"
    elif key == 'bursamktplace': 
        url = initial_urls[key] + stocks_dict[stock][3] + "/analystconsensus"
    elif key == 'reuters':
        url = initial_urls[key] + stocks_dict[stock][4] + "/profile"
    driver.get(url)
    

def get_trading_view_data(driver, stock):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, trading_view_monthly))).click()
    time.sleep(3)
    stock = stock
    platform = 'trading_view'
    try: 
        verdict = driver.find_element_by_xpath('//*[@id="technicals-root"]/div/div/div[2]/div[2]/span[2]').text
    except: 
        verdict = None
    try: 
        sell = driver.find_element_by_xpath('//*[@id="technicals-root"]/div/div/div[2]/div[2]/div[2]/div[1]/span[1]').text
    except: 
        sell = None
    try: 
        neutral = driver.find_element_by_xpath('//*[@id="technicals-root"]/div/div/div[2]/div[2]/div[2]/div[2]/span[1]').text
    except: 
        neutral = None
    try: 
        buy = driver.find_element_by_xpath('//*[@id="technicals-root"]/div/div/div[2]/div[2]/div[2]/div[3]/span[1]').text 
    except: 
        buy = None
    return stock, platform, verdict, sell, neutral, buy


def get_investing_data(driver, stock):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, investing_monthly))).click()
    time.sleep(3)
    stock = stock
    platform = 'investing'
    try: 
        verdict = driver.find_element_by_xpath('//*[@id="techStudiesInnerWrap"]/div[2]/span[2]').text
    except: 
        verdict = None
    try: 
        sell = driver.find_element_by_xpath('//*[@id="maSell"]').text
    except: 
        sell = None
    neutral = None
    try: 
        buy = driver.find_element_by_xpath('//*[@id="maBuy"]').text 
    except: 
        buy = None
    return stock, platform, verdict, sell, neutral, buy

def get_wsj_data(driver, stock):
    stock = stock
    platform = 'wsj'
    try: 
        verdict = driver.find_element_by_xpath('//*[@id="historicalCol"]/div[1]/div/table/tbody/tr[6]/td[4]/div/div/div').text
    except: 
        verdict = None
    try: 
        sell = driver.find_element_by_xpath('//*[@id="historicalCol"]/div[1]/div/table/tbody/tr[5]/td[4]/div/span[2]').text
    except: 
        sell = None
    try: 
        neutral = driver.find_element_by_xpath('//*[@id="historicalCol"]/div[1]/div/table/tbody/tr[3]/td[4]/div/span[2]').text
    except: 
        neutral = None
    try: 
        buy = driver.find_element_by_xpath('//*[@id="historicalCol"]/div[1]/div/table/tbody/tr[1]/td[4]/div/span[2]').text 
    except: 
        buy = None
    return stock, platform, verdict, sell, neutral, buy


def get_bursamktplace_data(driver, stock):
    stock = stock
    platform = 'bursamktplace'
    time.sleep(3)
    try: 
        verdict = driver.find_element_by_xpath('/html/body/main/div/div/div/section/div[2]/div[2]/div[2]/div/div[1]/div[2]/div').text
    except: 
        verdict = None
    try: 
        sell = driver.find_element_by_xpath('/html/body/main/div/div/section/section[2]/div[3]/div[2]/div[6]/div[2]').text
    except: 
        sell = None
    try: 
        neutral = driver.find_element_by_xpath('/html/body/main/div/div/section/section[2]/div[3]/div[2]/div[4]/div[2]').text
    except: 
        neutral = None
    try: 
        buy = driver.find_element_by_xpath('/html/body/main/div/div/section/section[2]/div[3]/div[2]/div[3]/div[2]').text 
    except: 
        buy = None
    return stock, platform, verdict, sell, neutral, buy


def get_reuters_data(driver, stock):
    stock = stock
    platform = 'reuters'
    try: 
        verdict = driver.find_element_by_xpath('//*[@id="__next"]/div/div[4]/div[1]/div/div/div/div[4]/div[3]/div[1]/div[1]').text
    except: 
        verdict = None
        
    sell = None
    neutral = None
    buy = None
    return stock, platform, verdict, sell, neutral, buy

def get_url(key, stock):
    if key == 'trading_view': 
        url = initial_urls[key] + stocks_dict[stock][0] + "/technicals"
    elif key == 'investing': 
        url = initial_urls[key] + stocks_dict[stock][1] + "-technical"
    elif key == 'wsj': 
        url = initial_urls[key] + stocks_dict[stock][2] + "/research-ratings"
    elif key == 'bursamktplace': 
        url = initial_urls[key] + stocks_dict[stock][3] + "/analystconsensus"
    elif key == 'reuters':
        url = initial_urls[key] + stocks_dict[stock][4] + "/profile"
    return url

#%% 
def get_data(driver, platform, stock, df):
    if platform == 'trading_view':
        open_website(driver, platform, stock)
        time.sleep(2)
        df.loc[len(df)] = get_trading_view_data(driver, stock)
    elif platform == 'investing':
        open_website(driver, platform, stock)
        time.sleep(2)
        df.loc[len(df)] = get_investing_data(driver, stock)
    elif platform == 'wsj':
        open_website(driver, platform, stock)
        time.sleep(2)
        df.loc[len(df)] = get_wsj_data(driver, stock)
    elif platform == 'bursamktplace':
        open_website(driver, platform, stock)
        time.sleep(2)
        df.loc[len(df)] = get_bursamktplace_data(driver, stock)
    elif platform == 'reuters':
        open_website(driver, platform, stock)
        time.sleep(2)
        df.loc[len(df)] = get_reuters_data(driver, stock)
    return df 


driver = get_driver('chromedriver.exe', user_agent_list)
df = pd.DataFrame(columns=['stock', 'platform', 'verdict', 'sell', 'neutral', 'buy'])

for stock in stocks_dict.keys():
    for platform in initial_urls.keys():
        get_data(driver, platform, stock, df)

#%% 
url_list = []
for stock in stocks_dict.keys():
    for platform in initial_urls.keys():
        url_list.append(get_url(platform, stock))

df['link'] = url_list     
