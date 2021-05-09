from random import randrange

from flask import Flask, request

import API
from Data.newsController import getNews

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
    prediction = model.predict(body['premise'], body['hypothesis'])
    return {"prediction": prediction}


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
@app.route('/', methods=["POST"])
def hello():
    body = request.get_json()
    return API.fetchNews(body)


if __name__ == "__main__":
    app.run()