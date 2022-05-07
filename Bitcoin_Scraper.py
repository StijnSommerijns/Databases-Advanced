from xmlrpc.client import DateTime
from bs4 import BeautifulSoup
from time import sleep
import requests
import pandas as pd
import pymongo as mongo
import json
import redis

client = mongo.MongoClient("mongodb://127.0.0.1:27017/")
database = client["databasesAdvanced"]
collection = database["bitcoinHashes"]

redis_client = redis.Redis(host="localhost", port="6379", db=0)

# Declaring empty dataframes for both all and highest bitcoin hashes
bitcoinDataFrame = pd.DataFrame(columns =['Hash', 'Time', 'Amount (BTC)', 'Amount (USD)'], dtype = float)
highestValuesDataFrame = pd.DataFrame(columns =['Hash', 'Time', 'Amount (BTC)', 'Amount (USD)'], dtype = float)

# Function for continuous scraping and data cleansing
def bitcoinScraper():
    # Making a GET request
    url = "https://www.blockchain.com/btc/unconfirmed-transactions"
    req = requests.get(url)
    # Parsing HTML
    soupBS = BeautifulSoup(req.text, features="html.parser")
    # Finding all div tags holding bitcoin information
    links = soupBS.find_all("div", {"class" : "sc-1g6z4xm-0 hXyplo"})

    #Declaring empty list
    list_of_divs = []

    # Putting content of div tags in previous declared list
    for link in links:
        list_of_divs.append(link.get_text())

    # Declaring new empty list
    bitcoin_list = []

    # Looping over list with div content and data cleansing
    for div in list_of_divs:
        div = div.replace("Hash", "")
        div = div.replace("Time", " ")
        div = div.replace("Amount (BTC)", " ")
        div = div.replace("Amount (USD)", " ")
        div = div.replace(" BTC", "_BTC")
        # Splitting the 'div' string into a list
        temp_list = list(div.split(" "))

        # Looping over elements of new list to clean final data
        for i in range(len(temp_list)):
            if "_BTC" in temp_list[i]:
                temp_list[i] = temp_list[i][:-4]
        # Adding the temporary list to the general 'bitcoin_list'
        bitcoin_list.append(temp_list)

    global bitcoinDataFrame
    # Declaring and initializing a temporary dataframe, populating it with the content of the 'bitcoin_list'
    # and reversing it so older records are on top
    bitcoinDataFrameTemp = pd.DataFrame(bitcoin_list, columns =['Hash', 'Time', 'Amount (BTC)', 'Amount (USD)']).iloc[::-1]
    # Joining the temporary dataframe to the big dataframe and removing any duplicate data
    bitcoinDataFrame = pd.concat([bitcoinDataFrame, bitcoinDataFrameTemp]).drop_duplicates().reset_index(drop=True)

    # Making sure the 'Amount (BTC)' data gets read as a float
    bitcoinDataFrame = bitcoinDataFrame.astype({'Amount (BTC)': 'float'})
    # Emptying the temporary dataframe
    bitcoinDataFrameTemp.drop(bitcoinDataFrameTemp.index, inplace=True)

# Function to extract highest hash value to text file
def highestPerMinute():
    global bitcoinDataFrame
    # Declaring and initializing the first timestamp from the dataframe
    startTime = bitcoinDataFrame["Time"].iloc[0]
    
    # Making a dataframe only consisting of data with the same value as 'startTime'
    startingMinuteDF = bitcoinDataFrame[bitcoinDataFrame["Time"] == startTime]
    # Sorting this dataframe so that the highest bitcoin value is on top
    startingMinuteDF.sort_values(by='Amount (BTC)', inplace=True, ascending=False)

    highestValue = startingMinuteDF.iloc[:1]
    highestValueJSON = highestValue.to_json(orient="records")

    # Removing all data from the big bitcoinDataFrame with the same value as startTime
    bitcoinDataFrame = bitcoinDataFrame[bitcoinDataFrame.Time != startTime]

    return highestValueJSON[1:-1]

counter = 0
while counter < 14:
    # Scraping the webpage
    bitcoinScraper()
    counter += 1
    #print(counter)
    # Triggers when 1 minute has passed
    if counter == 13:
        # Creates a key-value pair in Redis with an expiration of 59 seconds
        redis_client.set("bitcoin_hash", highestPerMinute(), ex=59)
        # Pushes the cashed key-value from Redis to MongoDB
        collection.insert_one(json.loads(redis_client.get("bitcoin_hash")))
        # Resets counter so loop can continue to run
        counter = 0
    # Waiting 4 seconds to scrape again
    sleep(4)