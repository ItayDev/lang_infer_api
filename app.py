from datetime import datetime
from flask import Flask, request, config
from API import API
from MyJsonEncoder import MyJsonEncoder
from data.NewsRequester import NewsRequester
from data.TweetsRequester import TWEET_DATE_FORMAT

app = Flask(__name__)
app.json_encoder = MyJsonEncoder
with app.app_context():
    config.api = API()

# This route returns a score of tweets' reliability for a tweeter account.
# the route argument is the account name and the route parameters are 'startDate' and 'endDate'
@app.route('/classify/<account_name>', methods=["GET"])
def run_hypothesis_model(account_name):
    return config.api.classify(account_name)


# This route returns a probability for a given text to be true according to detection of lying patterns.
# payload should be a list of a titles as follows:
# {
#   "titles":
#   [
#       "Today is Monday",
#       "Sure Barur"
#   ]
# }
@app.route('/patternModel', methods=["POST"])
def run_pattern_model():
    body = request.get_json()
    return config.api.run_pattern_model(body)


@app.route('/grade/pattern/<account_name>', methods=["GET"])
def grade_account_by_pattern_model(account_name: str):
    tweets = config.api.retrieve_tweets(account_name)
    return config.api.pattern_model_grader(tweets)


@app.route('/tweets/<person>', methods=["GET"])
def get_tweets(person):
    return {"tweets": config.api.retrieve_tweets(person)}


if __name__ == "__main__":
    app.run()
