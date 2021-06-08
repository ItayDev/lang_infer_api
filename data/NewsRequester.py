from json import JSONEncoder

import requests
from datetime import datetime
from pickle import dump, load
from flask import current_app as app
from credentials import NYT_API_KEY
import pytz
import os
import time

UTC = pytz.utc
ARTICLE_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
QUERY_DATE_FORMAT = "%Y-%m-%d"
API_KEY = NYT_API_KEY
API_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json?fq="
NEWS_CACHE_PATH = "news_cache"
NEWS_CACHE_FILE = "cache.pkl"
DOCS_PER_PAGE = 10
MAX_NUM_OF_PAGES = 100
REQUESTS_DELAY = 6


def read_all_articles(start_date, end_date, num_of_pages):
    articles = []
    try:
        for page in range(0, num_of_pages + 1):
            time.sleep(REQUESTS_DELAY)
            url = f'{API_URL}news_desk:("National" "Politics" "Foreign")' \
                  f'&begin_date={start_date.strftime(QUERY_DATE_FORMAT)}' \
                  f'&end_date={end_date.strftime(QUERY_DATE_FORMAT)}]' \
                  f'&api-key={API_KEY}' \
                  f'&page={page}' \
                  f'&sort=newest'
            res = requests.get(url).json()

            articles += list(
                map(
                    lambda article: Article(
                        datetime.strptime(article['pub_date'], ARTICLE_DATE_FORMAT).replace(tzinfo=None),
                        article['headline']['main'],
                        article['abstract'],
                        article['web_url']
                    ),
                    res["response"]["docs"]
                )
            )
    except:
        print("Couldn't fetch all the articles")
    finally:
        return articles


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
                           start_date <= article.publish_date <= end_date,
                           self.articles))

    def request_news_published_at(self, publish_date):
        if publish_date > self.end_date:
            self.prefetch_articles(self.end_date, publish_date)
        if publish_date < self.start_date:
            self.prefetch_articles(publish_date, self.start_date)

        return list(filter(lambda article:
                           article.publish_date.date() == publish_date.date(),
                           self.articles))

    def prefetch_articles(self, start_date, end_date):
        if self.start_date is None or self.end_date is None:
            self.start_date = start_date
            self.end_date = end_date
            self.__request_nyt_api(start_date, end_date)
        if end_date > self.end_date:
            self.__request_nyt_api(self.end_date, end_date)
        if start_date < self.start_date:
            self.__request_nyt_api(start_date, self.start_date)

    def __request_nyt_api(self, start_date, end_date):
        self.start_date = min(self.start_date, start_date)
        self.end_date = max(self.end_date, end_date)

        url = f'{API_URL}news_desk:("National" "Politics" "Foreign")' \
              f'&begin_date={start_date.strftime(QUERY_DATE_FORMAT)}' \
              f'&end_date={end_date.strftime(QUERY_DATE_FORMAT)}]' \
              f'&api-key={API_KEY}'
        res = requests.get(url).json()
        hits = res['response']['meta']['hits']
        number_of_pages = min(int(hits / DOCS_PER_PAGE), MAX_NUM_OF_PAGES)
        all_articles = read_all_articles(start_date, end_date, number_of_pages)
        oldest_article_date = min([article.publish_date for article in all_articles])

        # In case not all articles were actually fetched
        if oldest_article_date > self.start_date:
            self.start_date = oldest_article_date

        self.articles += all_articles
        self._cache_results()

    def _cache_results(self):
        cache_dir_path = os.path.join(app.instance_path, NEWS_CACHE_PATH)
        cache_file_path = os.path.join(app.instance_path, NEWS_CACHE_PATH, NEWS_CACHE_FILE)
        if not os.path.exists(cache_dir_path):
            os.makedirs(cache_dir_path, exist_ok=True)
        with open(cache_file_path, 'wb') as file:
            dump({'start_date': self.start_date,
                  'end_date': self.end_date,
                  'articles': self.articles}, file)

    def _load_cache(self):
        cache_file_path = os.path.join(app.instance_path, NEWS_CACHE_PATH, NEWS_CACHE_FILE)
        if os.path.exists(cache_file_path):
            with open(cache_file_path, 'rb') as file:
                cache = load(file)
                self.start_date = cache['start_date']
                self.end_date = cache['end_date']
                self.articles = cache['articles']


class Article(JSONEncoder):
    def __init__(self, publish_date, title, text, url):
        self.publish_date = publish_date
        self.title = title
        self.text = text
        self.url = url

    def default(self, obj):
        if isinstance(obj, Article):
            return obj.__dict__
        return super(JSONEncoder, self).default(obj)
