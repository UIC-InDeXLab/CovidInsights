# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 12:57:01 2020

@author: kaush
"""
#This code collects the data for every country as updated on world-o-meter
from selenium import webdriver
from bs4 import BeautifulSoup
import time
from datetime import datetime
import sqlite3
from selenium.webdriver.chrome.options import Options
import urllib.request
from datetime import datetime
# import shutil
from selenium.webdriver.common.action_chains import ActionChains

now = datetime.now()    #this is to get the date and time of data collection
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
print(dt_string)
def output(data):   #This will store the data into a csv file in desired format
    """f.write("COUNTRY "+data[0].text+"\n")
    f.write("Total Cases "+data[1].text+"\n")
    f.write("New Cases "+data[2].text+"\n")
    f.write("Total Deaths "+data[3].text+"\n")
    f.write("New Deaths "+data[4].text+"\n")
    f.write("Total Recovered "+data[5].text+"\n")
    f.write("Active Cases "+data[6].text+"\n")
    f.write("Serious/Critical "+data[7].text+"\n")
    f.write("Total Cases/ 1M Population "+data[8].text+"\n")
    f.write("Deaths/ 1M Population "+data[9].text+"\n")
    f.write("Total Tests "+data[10].text+"\n")
    f.write("Tests/ 1M Population "+data[11].text+"\n")
    f.write("___________________________________________________________\n")"""
    if(len(data[0].text)>=3):
        f.write(dt_string+","+data[0].text.replace(',','')+","+data[1].text.replace(',','')+","+data[2].text.replace(',','')+","+data[3].text.replace(',','')+","
                +data[4].text.replace(',','')+","+data[5].text.replace(',','')+","+data[6].text.replace(',','')+","+
                data[7].text.replace(',','')+","+data[8].text.replace(',','')+","+data[9].text.replace(',','')+","+
                data[10].text.replace(',','')+","+data[11].text.replace(',','')+"\n")

browser = webdriver.Chrome("C:/Users/kaush/OneDrive/Desktop/web_crawler/twitter_crawler/chromedriver.exe") #Install chromedriver to run this code and put the appropriate address
url = "https://www.worldometers.info/coronavirus/" #Collecting data from this URL
browser.get(url)
table = browser.find_element_by_tag_name("table")
soup = BeautifulSoup(browser.page_source, 'html.parser')
items = soup.find_all("tr")[1:221]
f=open("worldwide_cases.csv","w+") #Data will be stored in this file.
for item in items:
    data= item.find_all("td")
    name=data[0].text.lower()
    name=name.strip()
    if(name=="world" or name=="europe" or name=="north america" or name=="asia" or name=="oceania" or name=="africa" or name=="south america" ): #Excluding the data from continents and using the data from countries
        print(name)
        #print(len(name))
    else:
        output(data)
        
        #print (data[-1])
    #print (name)
    #print(data[1].text)
#print(items)
f.close()
browser.close()
