# Databases-Advanced
## Installing Ubuntu
Download Ubuntu 20.04 LTS for your virtual machine

Create a new virtual machine with preferably more than 8GB of RAM and 50GB of hard drive

Installation/configuration of virtual machine is personal preference
## Installing Python 3 on VM
Run following commands to install python:

`$ sudo apt update`

`$ sudo apt -y upgrade`

`$ sudo apt-get install python3`

`$ sudo apt install -y python3-pip`

`$ mkdir Python_Scripts`

## Installing packages for scraper
Run following commands to install **BeautifulSoup**

`$ sudo apt-get install python3-bs4`


*You can very if it is correctly installed with this command*: 
`$ python3 -m pip show beautifulsoup4`

Installation of **Requests**

`$ python -m pip install requests`

Installing **pandas**

`$ sudo apt-get install python3-pandas`

Installing the **PyMongo** module for MongoDB

`sudo apt-get install python3-pymongo`

Installation of **Redis** module

`python3 –m pip install redis`

## Installing MongoDB
This code can be found in the bash file named "MongoDB-script"

`wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add –`

`sudo apt update`

`echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list`

`sudo apt-get update`

`sudo apt-get install -y mongodb-org`

`sudo systemctl start mongod`

`systemctl status mongod`

`sudo systemctl enable mongod`

To access the mongo shell, type "mongo" in the terminal
## Installing Redis
This code can be found in the bash file named "Redis-script"

`sudo apt update`

`sudo apt install redis-server`

To access the Redis shell, type "redis-cli" in the terminal
