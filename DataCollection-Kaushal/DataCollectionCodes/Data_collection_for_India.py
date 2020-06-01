# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 09:08:00 2020

@author: kaush
"""

from selenium import webdriver
from bs4 import BeautifulSoup
import time
from datetime import datetime
import sqlite3
from selenium.webdriver.chrome.options import Options
import urllib.request
# import shutil
from selenium.webdriver.common.action_chains import ActionChains

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
# browser = webdriver.Chrome("/usr/bin/chromedriver", options=options)
browser = webdriver.Chrome("C:/Users/kaush/OneDrive/Desktop/web_crawler/twitter_crawler/chromedriver.exe")
# browser = webdriver.Chrome("C:/workspace/chromedriver.exe")
# browser = webdriver.Chrome("E:\chromedriver_win32\chromedriver.exe")

now = datetime.now()

"""for city in placeName.values():
    if city not in oldCity.values():
        cursor.execute("ALTER TABLE virus ADD [" + city + "] CHAR(20);")"""
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
citynames = []
# browser = webdriver.Chrome("/Users/FengyuXu/Desktop/web_crawler/twitter_crawler/chromedriver") #fengyu's chromefrive location
#browser = webdriver.Chrome("C:\Workspace\chromedriver.exe") # zhaobo's chromedrive location'


# # China Provinces
#
url = "https://www.mohfw.gov.in"
browser.get(url)
f=open("Data_India.csv","w+")
table = browser.find_element_by_tag_name("table")
soup = BeautifulSoup(browser.page_source, 'html.parser')
items = soup.find_all("tr")[1:-4]
#death="100"
for item in items:
    data = item.find_all("td")
    #name = data[1].text.lower()
    f.write(dt_string+','+str(data[1].text)+','+str(data[3].text)+','+str(data[3].text)+','+str(data[4].text)+','+"\n")
f.close()
browser.close()
