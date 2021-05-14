import requests
from datetime import datetime
from pickle import dump, load
import pytz
import os

UTC = pytz.utc
ARTICLE_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
QUERY_DATE_FORMAT = "%Y-%m-%d"
API_KEY = "mkmf1ZFfJzxR1gmt2GUW0JppZXKDHg9M"
API_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json?fq="
NEWS_CACHE_PATH = "news_cache"
NEWS_CACHE_FILE = "cache.pkl"


class NewsRequester:
    def __init__(self):
        self.start_date = None
        self.end_date = None
        self.articles = []
        self._load_cache()

    def request_news(self, start_date, end_date):
        if self.start_date is None or self.end_date is None:
            self.prefetch_articles(start_date, end_date)
        if start_date < self.start_date:
            self.prefetch_articles(start_date, self.start_date)
        if end_date > self.end_date:
            self.prefetch_articles(end_date, self.end_date)

        return list(filter(lambda article:
                           UTC.localize(start_date) <= datetime.strptime(article['pub_date'], ARTICLE_DATE_FORMAT) <= UTC.localize(end_date),
                           self.articles))

    def prefetch_articles(self, start_date, end_date):
        should_fetch = False
        if self.start_date is None or self.end_date is None:
            self.start_date = start_date
            self.end_date = end_date
            should_fetch = True
        if start_date < self.start_date:
            self.start_date = start_date
            should_fetch = True
        if end_date > self.end_date:
            self.end_date = end_date
            should_fetch = True
        if should_fetch:
            url = f'{API_URL}news_desk:("Media" "National" "Politics" "Foreign")' \
                  f'&begin_date={start_date.strftime(QUERY_DATE_FORMAT)}' \
                  f'&end_date={end_date.strftime(QUERY_DATE_FORMAT)}]' \
                  f'&api-key={API_KEY}'
            res = requests.get(url)
            self.articles += (res.json())["response"]["docs"]
            self._cache_results()

    def _cache_results(self):
        if not os.path.exists(NEWS_CACHE_PATH):
            os.mkdir(NEWS_CACHE_PATH)
        with open(f'{NEWS_CACHE_PATH}/{NEWS_CACHE_FILE}', 'wb') as file:
            dump({'start_date': self.start_date,
                  'end_date': self.end_date,
                  'articles': self.articles}, file)

    def _load_cache(self):
        if os.path.exists(f'{NEWS_CACHE_PATH}/{NEWS_CACHE_FILE}'):
            with open(f'{NEWS_CACHE_PATH}/{NEWS_CACHE_FILE}', 'rb') as file:
                cache = load(file)
                self.start_date = cache['start_date']
                self.end_date = cache['end_date']
                self.articles = cache['articles']

