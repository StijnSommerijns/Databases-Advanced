from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from time import sleep
import requests
import pymongo as mongo
import json
import redis

# Using the pymongo module to connect to MongoDB
client = mongo.MongoClient("mongodb://127.0.0.1:27017/")
# Making database and collection
database = client["databasesAdvanced"]
collection = database["bitcoinHashes"]

# Using the redis module to connect to redis
redis_client = redis.Redis(host="localhost", port="6379", db=0)

# Declaring empty list to store hashes before exporting to redis
list_of_hashes = []

# Function for continuous scraping and data cleansing
def bitcoinScraper():
    # Making a GET request
    url = "https://www.blockchain.com/btc/unconfirmed-transactions"
    req = requests.get(url)
    # Parsing HTML
    soupBS = BeautifulSoup(req.text, features="html.parser")
    # Finding all div tags holding bitcoin information
    links = soupBS.find_all("div", {"class" : "sc-1g6z4xm-0 hXyplo"})

    #Declaring empty list for content of div tags
    list_of_divs = []

    # Putting content of div tags in previous declared list
    for link in links:
        list_of_divs.append(link.get_text())

    # Looping over reversed list with div content and data cleansing
    for div in reversed(list_of_divs):
        div = div.replace("Hash", "")
        div = div.replace("Time", " ")
        div = div.replace("Amount (BTC)", " ")
        div = div.replace("Amount (USD)", " ")
        div = div.replace(" BTC", "_BTC")
        # Splitting the 'div' string into a list
        temp_list = list(div.split(" "))

        # Adjusting scraped time to local time
        timestamp = datetime.strptime(temp_list[1], "%H:%M") + timedelta(hours=2)
        temp_list[1] = timestamp.strftime("%H:%M")
        
        # Looping over elements of new list to clean final data
        for i in range(len(temp_list)):
            if "_BTC" in temp_list[i]:
                temp_list[i] = float(temp_list[i][:-4])
                break
        # Adding the temp_list to list_of_hashes without duplicates
        if temp_list not in list_of_hashes:
            list_of_hashes.append(temp_list)

# Function to send all hashes of the same minute to redis and returns key of hashes that have been pushed
def highestPerMinute():
    global list_of_hashes
    
    # Getting timestamp for first set of hashes
    timestamp = list_of_hashes[0][1]
    columns = ['Hash', 'Time', 'Amount (BTC)', 'Amount (USD)']
    # Populating list with dictionary of first hash as reference to compare bitcoin value
    timestamp_list = [dict(zip(columns, list_of_hashes[0]))]

    # Looping over list_of_hashes to find what hashvalue is the highest
    for i in range(len(list_of_hashes))[1:]:
        # Only checking the hashes of the current timestamp
        if timestamp == list_of_hashes[i][1]:
            redisValue = dict(zip(columns, list_of_hashes[i]))
            # If hash is bigger it gets inserted as first element of redis list
            if redisValue["Amount (BTC)"] >= timestamp_list[0]["Amount (BTC)"]:
                timestamp_list.insert(0, redisValue)
            # Else just add the value as last element
            else:
                timestamp_list.append(redisValue)

    # After all values of the timestamp have been pushed into the redis list, they get deleted from our list_of_hashes
    timestamp_listLength = len(timestamp_list)
    del list_of_hashes[0:timestamp_listLength]

    # Pushes to redis with the timestamp as key and the list as value
    for i in range(len(timestamp_list)):
        redis_client.rpush(timestamp, json.dumps(timestamp_list[i]))
        # 60 seconds expiration on key
        redis_client.expire(timestamp, 60)
    return timestamp

counter = 0
while counter < 15:
    # Scraping the webpage
    bitcoinScraper()
    counter += 1
    # Triggers when 1 minute has passed
    if counter == 14:
        # Get returned the timestamp which is key
        redisKey = highestPerMinute()
        # lrange to find first element of list
        largestHash = redis_client.lrange(redisKey, 0, 0)
        largestHash = str(largestHash)[3:-2]
        # Pushing highest hash to MongoDB collection
        collection.insert_one(json.loads(largestHash))
        print("Highest hashvalue of " + redisKey + " has been stored in MongoDB")
        # Resets counter so loop can continue to run
        counter = 0
    # Waiting 4 seconds to scrape again
    sleep(4)