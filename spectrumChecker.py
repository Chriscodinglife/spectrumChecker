#!/usr/bin/python2.7

#### Christian Orellana
#### June 2020
#### Speed Test Hourly Checks


'''
  /$$$$$$  /$$                 /$$          
 /$$__  $$| $$                |__/          
| $$  \__/| $$$$$$$   /$$$$$$  /$$  /$$$$$$$
| $$      | $$__  $$ /$$__  $$| $$ /$$_____/
| $$      | $$  \ $$| $$  \__/| $$|  $$$$$$ 
| $$    $$| $$  | $$| $$      | $$ \____  $$
|  $$$$$$/| $$  | $$| $$      | $$ /$$$$$$$/
 \______/ |__/  |__/|__/      |__/|_______/ 
                                     
                                            

This script is designed to run hourly and append Speedtest cli results to a local csv file
and then post onto Twitter a gif based on the speed results.

This is using Twurl to post to Twitter and runs on a cron job to run hourly.
'''


### IMPORT       
import tweepy  
import random  
import pandas as pd
from datetime import datetime, time
from subprocess import check_output
import os
import numpy as np
import random
import matplotlib.pyplot as plt 


### GLOBAL VARIABLES
now = datetime.now()
hour = now.strftime('%H:%M')
date = now.strftime('%A_%B_%d_%Y')
dateNoBars = now.strftime('%A %B %d %Y')
csvLocation = '/home/flexorflux/Desktop/spectrumChecker/data/{}.csv'.format(date)
downloadSpeed = 0

### FUNCTIONS
def createCSV():
  
  "Create a csv file if it doesn't exist"
  if os.path.exists(csvLocation):
    pass
  else:
    data = {}
    columns = ["time", "server name", "server id", "latency", "jitter", "packet loss", "download", "upload", "download bytes", "upload bytes", "share url"]
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(csvLocation, index=False)
    
def speedList():
  
  "Run the Speedtest with the CLI"
  bashOutput = check_output(['/usr/bin/speedtest', '-s', '16888', '-f', 'csv'])
  bashOuttoList = list(bashOutput.split(","))
  bashOuttoList = [i.replace('"', '') for i in bashOuttoList]
  bashOuttoList.insert(0, hour)
  bashOuttoList.remove(' NY')
  return bashOuttoList
  
def appendSpeedList():
  
  "Take the speedtest results and add it to the csv file"
  df = pd.read_csv(csvLocation)
  df.loc[len(df)] = speedList()
  df['download'] = df['download'].astype(int)
  df.to_csv(csvLocation, index=False)
  
def evaluateAndTweet():
  
  "Bash or Compliment Spectrum based on the results"
  consumerKey = ''
  consumerSecret = '' 
  accessToken = '' 
  accessTokenSecret = '' 
  
  auth = tweepy.OAuthHandler(consumerKey, consumerSecret)  
  auth.set_access_token(accessToken, accessTokenSecret)  
  api = tweepy.API(auth)  
  
  df = pd.read_csv(csvLocation)
  downloadSpeed = df['download'].iloc[-1]
  downloadSpeed = (downloadSpeed / 1048576).round(decimals=0)
  
  fileNumber = random.randint(1,10)

  if downloadSpeed >= 40:
    tweet = "Nice job #Spectrum! My internet speed is at {}MBps, you guys are awesome!".format(downloadSpeed)
    media = api.media_upload("/home/flexorflux/Desktop/spectrumChecker/images/hellyea/hellyea{}.gif".format(fileNumber))
    api.update_status(status=tweet, media_ids=[media.media_id])
  elif downloadSpeed in range(20, 40):
    tweet = "I guess it's decent #Spectrum, my internet could be a tad better though since it's at {}MBps".format(downloadSpeed)
    media = api.media_upload("/home/flexorflux/Desktop/spectrumChecker/images/couldBeBetter/better{}.gif".format(fileNumber))
    api.update_status(status=tweet, media_ids=[media.media_id])
  else:
    tweet = "#Spectrum? wtf is going on with my internet? it's at {}MBps...".format(downloadSpeed)
    media = api.media_upload("/home/flexorflux/Desktop/spectrumChecker/images/wtf/wtf{}.gif".format(fileNumber))
    api.update_status(status=tweet, media_ids=[media.media_id])

def convertToMB(x):
  
  return x / 1048576
  
  print("converted")

def createPlot():
  
  "Check if its the end of the day and create a plot with data of the data"
  df = pd.read_csv(csvLocation)
  lastHour = df['time'].iloc[-1]
  lastHour = datetime.strptime(lastHour, "%H:%M")
  df['download'] = df['download'].apply(convertToMB)
  averageInternet = df['download'].mean()
  averageInternet = averageInternet.round(decimals=0)
  
  if lastHour >= datetime.strptime("23:00","%H:%M"):
    plt.plot(df['time'], df['download'])
    plt.xlabel("Time of Day")
    plt.ylabel("Internet Speed (MBps)")
    plt.title("My Home's Internet Speed for {}".format(dateNoBars))
    plt.xticks(rotation=30, fontsize=5)
    plt.savefig("/home/flexorflux/Desktop/spectrumChecker/plots/{}.png".format(date))
    
    consumerKey = ''
    consumerSecret = '' 
    accessToken = '' 
    accessTokenSecret = '' 
  
    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)  
    auth.set_access_token(accessToken, accessTokenSecret)  
    api = tweepy.API(auth)
    
    tweet = "Hey #Spectrum, just FYI, here are my speed results for today, {}, with an average of {} MBps.".format(dateNoBars, averageInternet)
    media = api.media_upload("/home/flexorflux/Desktop/spectrumChecker/plots/{}.png".format(date))
    api.update_status(status=tweet, media_ids=[media.media_id])
    

### EXECUTE

createCSV()
appendSpeedList()
evaluateAndTweet()
createPlot()

