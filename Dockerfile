FROM python:3.10

ADD Bitcoin_Scraper.py .

RUN pip install beautifulsoup4 requests pymongo redis

CMD [ "python", "./Bitcoin_Scraper.py" ]