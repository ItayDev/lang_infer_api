import tweepy
import credentials
import preprocessor as p
CONSUMER_KEY = credentials.TWITTER_API_KEY
CONSUMER_SECRET = credentials.TWITTER_API_SECRET_KEY
ACCESS_TOKEN = credentials.TWITTER_ACCESS_TOKEN
ACCESS_TOKEN_SECRET = credentials.TWITTER_ACCESS_TOKEN_SECRET
MAX_TWEETS_RETURN = 20


def clean_tweet(tweet_text: str):
    return p.clean(tweet_text)


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

    def fetch_tweets_from_server(self, screen_name: str, start_date=None, end_date=None):
        return self.api.user_timeline(screen_name=screen_name, tweet_mode="extended",  count=MAX_TWEETS_RETURN)
