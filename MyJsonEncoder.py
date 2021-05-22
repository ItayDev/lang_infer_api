from datetime import datetime
from data import TweetsRequester
from flask.json import JSONEncoder


class MyJsonEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime(TweetsRequester.TWEET_DATE_FORMAT)
        return o.__dict__
