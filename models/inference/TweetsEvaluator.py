from models.inference.predict import LangInferModelWrapper

from datetime import datetime, timedelta

from data.NewsRequester import NewsRequester

ARTICLE_PREFETCH_AMOUNT = 7
# TODO: find what is the correct tweet date's format
TWEET_DATE_FORMAT = '%Y-%m-%d'

class TweetsEvaluator:
    def __init__(self, model: LangInferModelWrapper, news_requester: NewsRequester):
        self.model = model
        self.news_requester = news_requester

    def eval_tweets(self, tweets):
        self._prefetch_articles(tweets)

        return list(map(self._eval_tweet, tweets))

    def _eval_tweet(self, tweet):
        tweet_date = datetime.strptime(tweet['date'], TWEET_DATE_FORMAT)
        tweet_content = tweet['content']
        articles_start_date = tweet_date - timedelta(days=ARTICLE_PREFETCH_AMOUNT)
        articles_end_date = tweet_date + timedelta(days=ARTICLE_PREFETCH_AMOUNT)

        articles = self.news_requester.request_news(articles_start_date, articles_end_date)

        articles_with_scores = list(map(lambda article: {
            'article': article,
            'score': self.model.predict([{'premise': article['abstract'], 'hypothesis': tweet_content}])[0]
        }, articles))

        entailments = list(filter(lambda article: article['score'] > 0.7, articles_with_scores))
        contradictions = list(filter(lambda article: article['score'] < 0.3, articles_with_scores))

        res = []

        if len(entailments) > 0:
            res.append(max(entailments, key=lambda article: article['score']))
        if len(contradictions) > 0:
            res.append(min(contradictions, key=lambda article: article['score']))

        return res

    def _prefetch_articles(self, tweets):
        dates = [datetime.strptime(tweet['date'], TWEET_DATE_FORMAT) for tweet in tweets]
        start_date = min(dates) - timedelta(days=ARTICLE_PREFETCH_AMOUNT)
        end_date = max(dates) + timedelta(days=ARTICLE_PREFETCH_AMOUNT)

        self.news_requester.prefetch_articles(start_date, end_date)
