# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 18:41:19 2020

@author: kaush
"""
#This code collects the data from newyork times and stores it in a csv file.
#If this code run everyday, we will have a file that contains the standardized data for each county in every state
import urllib, json
from datetime import datetime
#import urllib, json
import re
import requests
from bs4 import BeautifulSoup
u="https://www.nytimes.com/interactive/2020/us/coronavirus-us-cases.html"   #url for downloading data
request= requests.get(u)    #opening url
#print(request.status_code)  #gets the status code
soup = BeautifulSoup(request.text, "html.parser")   #read the source code in html format
each=soup.findAll('script')[-11]    #Looks for the designated json file that has the data
a=re.findall(r'"([^"]*)"', str(each))[0]    #Filters out the link to json file
#print(a)    #prints the link

url = a
now = datetime.now()
response = urllib.request.urlopen(url)
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
data = json.loads(response.read())
data_1=data['data']
f=open("detailed_US_data.csv","a+")
geo=dict()  #This is a list to store the geo-id of each state, This is further used to map the counties to corrosponding states on the basis of geo-id
for each in data_1:
    #print (each['geoid'][4:6])
    if each['region_type']=='state':
        k=each['geoid'][-2:]
        #print (k)
        if k not in geo:
            geo.update({k:each['display_name']})
#print(geo)
for each in data_1:     #This stored the relevant data into a csv file with the respective geo-ids'
    #f.write(each['region_type']+"\n")
    d=each['geoid'][4:6]
    if(each['region_type']=="county" and d in geo):
        f.write(dt_string+','+each['geoid']+','+each['display_name'].replace(',','')+","+each['region_type']+","+str(each['cases'][-1])+','+str(each['deaths'][-1])+","+geo[d]+"\n")
    else:
        f.write(dt_string+','+each['geoid']+','+each['display_name'].replace(',','')+","+each['region_type']+","+str(each['cases'][-1])+','+str(each['deaths'][-1])+"\n")
print (data_1[1])
f.close()
