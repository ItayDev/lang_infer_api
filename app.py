from flask import Flask, request, jsonify, json
from flask_cors import CORS
from random import randrange

from model.predict import Model
from newsController import getNews

app = Flask(__name__)
CORS(app)

# model = Model("saved_models/510250_snli-0.733-0.811_mnli_matched-0.601-0.933_mnli_mismatched-0.608-0.925"
#               ".9258981491734342")


@app.route('/', methods=["POST"])
def hello():
    body = request.get_json()
    print(body)
    prediction = randrange(100) # TODO get prediction from getNews
    print(getNews(body['news']))
    #model.predict(body['premise'], body['hypothesis'])
    return  {"prediction": prediction}
