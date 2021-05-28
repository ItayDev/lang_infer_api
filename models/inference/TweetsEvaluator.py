from typing import List

from data.TweetsRequester import Tweet
from models.inference.predict import LangInferModelWrapper
from datetime import timedelta
from data.NewsRequester import NewsRequester

ARTICLE_PREFETCH_AMOUNT = 7


class TweetsEvaluator:
    def __init__(self, inference_model: LangInferModelWrapper, news_requester: NewsRequester):
        self.inference_model = inference_model
        self.news_requester = news_requester

    def eval_tweets(self, tweets: List[Tweet]):
        self._prefetch_articles(tweets)

        return list(
            filter(
                lambda tweet_with_article: len(tweet_with_article["articles"]) > 0,
                map(self._eval_tweet_with_news, tweets)
            )
        )

    def _eval_tweet_with_news(self, tweet: Tweet):
        articles_start_date = tweet.date - timedelta(days=ARTICLE_PREFETCH_AMOUNT)
        articles_end_date = tweet.date + timedelta(days=ARTICLE_PREFETCH_AMOUNT)

        articles = self.news_requester.request_news(articles_start_date, articles_end_date)

        articles_with_scores = list(map(lambda article: {
            'article': article,
            'score': self.inference_model.predict([{
                'premise': article.text,
                'hypothesis': tweet.clean_content}])[0]
        }, articles))

        entailments = list(filter(lambda article: article['score'] > 0.7, articles_with_scores))
        contradictions = list(filter(lambda article: article['score'] < 0.3, articles_with_scores))

        significant_articles = []

        if len(entailments) > 0:
            significant_articles.append(max(entailments, key=lambda article: article['score']))
        if len(contradictions) > 0:
            significant_articles.append(min(contradictions, key=lambda article: article['score']))

        return {"tweet": tweet.raw_content, "articles": significant_articles}

    def _prefetch_articles(self, tweets: List[Tweet]):
        dates = [tweet.date for tweet in tweets]
        start_date = min(dates) - timedelta(days=ARTICLE_PREFETCH_AMOUNT)
        end_date = max(dates) + timedelta(days=ARTICLE_PREFETCH_AMOUNT)

        self.news_requester.prefetch_articles(start_date, end_date)
