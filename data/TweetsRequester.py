import datetime
import tweepy
import credentials
import preprocessor as p
from flask.json import JSONEncoder
import re
import emoji

CONSUMER_KEY = credentials.TWITTER_API_KEY
CONSUMER_SECRET = credentials.TWITTER_API_SECRET_KEY
ACCESS_TOKEN = credentials.TWITTER_ACCESS_TOKEN
ACCESS_TOKEN_SECRET = credentials.TWITTER_ACCESS_TOKEN_SECRET

# Maximum amounts of tweets returned by twitter server.
# Amounts of tweets could be even lower than this parameter, due to:
# twitter send less tweets than max, date filter applied...
MAX_TWEETS_RETURN = 15

TWEET_DATE_FORMAT = '%Y-%m-%d'


def clean_tweet(tweet_text: str):
    tweet_text = re.sub("@[A-Za-z0-9]+", "", tweet_text)  # Remove @ sign
    tweet_text = re.sub(r"(?:\@|http?\://|https?\://|www)\S+", "", tweet_text)  # Remove http links
    tweet_text = " ".join(tweet_text.split())
    tweet_text = ''.join(c for c in tweet_text if c not in emoji.UNICODE_EMOJI)  # Remove Emojis
    tweet_text = tweet_text.replace("#", "").replace("_", " ")  # Remove hashtag sign but keep the text

    return tweet_text


def filter_by_date(tweets, start_date: int = None, end_date: int = None):
    if start_date is not None:
        tweets = filter(lambda tweet: tweet.created_at > start_date, tweets)

    if end_date is not None:
        tweets = filter(lambda tweet: tweet.created_at < end_date, tweets)

    return list(tweets)


class TweetsRequester:

    def __init__(self):
        # Authenticate to Twitter
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

        # Create API object
        self.api = tweepy.API(auth)
        if self.api.verify_credentials():
            print("Credentials for twitter server OK")
        else:
            print("Error during authentication to twitter server")

    def fetch_tweets_from_server(self, screen_name: str):
        tweets = self.api.user_timeline(screen_name=screen_name, tweet_mode="extended",  count=MAX_TWEETS_RETURN)

        return [Tweet(tweet.full_text, tweet.created_at) for tweet in tweets]


class Tweet(JSONEncoder):
    def __init__(self, content, date):
        self.raw_content = content
        self.clean_content = clean_tweet(content)
        self.date = date

    def default(self, obj):
        if isinstance(obj, Tweet):
            return obj.__dict__
        return super(JSONEncoder, self).default(obj)


