from flask import Flask, request
import API

app = Flask(__name__)


# This route returns a probability for a given hypothesis to be inferred by a given premise.
# payload should be a list of a dictionary as follows:
# [
#   {
#       "premise":"Today is Monday",
#       "hypothesis":"Tomorrow will be Tuesday"
#   },
#   {
#       "premise": "Our grade is 100",
#       "hypothesis":"Sure barur"
#   }
# ]
@app.route('/hypothesisModel', methods=["POST"])
def run_hypothesis_model():
    body = request.get_json()
    return API.run_hypothesis_model(body)


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