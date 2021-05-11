from flask import Flask, request
import API

app = Flask(__name__)


# This route returns a score of tweets' reliability for a tweeter account.
# payload should contain tweeter account name as well as range of tweets (up to two months):
# {
#   "accountName": "BlufferDude",
#   "startDate": "2021-03-12"
#   "endDate": "2021-03-31"
# }
@app.route('/classify', methods=["POST"])
def run_hypothesis_model():
    body = request.get_json()
    tweets = None                           # TODO get the tweets, call API.evaluate_tweets_with_news only after being
    return API.evaluate_tweets_with_news()  # evaluated by the pattern model and filtered


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


# Sample Model for getting prediction from news
@app.route('/fetchNews', methods=["POST"])
def fetch_news():
    query = request.get_json()["query"]
    return API.fetch_news(query)


@app.route('/filterResults', methods=["POST"])
def pattern_model_filter():
    body = request.get_json()
    return API.pattern_model_filter(body)


if __name__ == "__main__":
    app.run()
