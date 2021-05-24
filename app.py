from datetime import datetime
from flask import Flask, request
import API
from MyJsonEncoder import MyJsonEncoder
from data.TweetsRequester import TWEET_DATE_FORMAT

app = Flask(__name__)
app.json_encoder = MyJsonEncoder

# This route returns a score of tweets' reliability for a tweeter account.
# the route argument is the account name and the route parameters are 'startDate' and 'endDate'
@app.route('/classify/<account_name>', methods=["GET"])
def run_hypothesis_model(account_name):
    try:
        start_date = datetime.strptime(request.args['startDate'], TWEET_DATE_FORMAT) \
            if 'start_date' in request.args else None

        end_date = datetime.strptime(request.args['endDate'], TWEET_DATE_FORMAT) \
            if 'end_date' in request.args else None

    except ValueError as e:
        return str(e), 400

    return API.classify(account_name, start_date, end_date)


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
    return API.run_pattern_model(body)


@app.route('/grade/pattern/<account_name>', methods=["GET"])
def grade_account_by_pattern_model(account_name: str):
    try:
        start_date = datetime.strptime(request.args['startDate'], TWEET_DATE_FORMAT) \
            if 'start_date' in request.args else None

        end_date = datetime.strptime(request.args['endDate'], TWEET_DATE_FORMAT) \
            if 'end_date' in request.args else None

    except ValueError as e:
        return str(e), 400

    tweets = API.retrieve_tweets(account_name, start_date, end_date)
    return API.pattern_model_grader(tweets)


# Sample Model for getting prediction from news
@app.route('/fetchNews', methods=["POST"])
def fetch_news():
    query = request.get_json()["query"]
    return API.fetch_news(query)


@app.route('/filterResults', methods=["POST"])
def pattern_model_filter():
    body = request.get_json()
    return API.pattern_model_filter(body)


@app.route('/tweets/<person>', methods=["GET"])
def get_tweets(person):
    try:
        start_date = datetime.strptime(request.args['start_date'], TWEET_DATE_FORMAT) \
            if 'start_date' in request.args else None

        end_date = datetime.strptime(request.args['end_date'], TWEET_DATE_FORMAT) \
            if 'end_date' in request.args else None

    except ValueError as e:
        return str(e), 400

    return {"tweets": API.retrieve_tweets(person, start_date, end_date)}


if __name__ == "__main__":
    app.run()
