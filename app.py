from flask import Flask, request, jsonify, json
from model.predict import Model

app = Flask(__name__)

model = Model("saved_models/510250_snli-0.733-0.811_mnli_matched-0.601-0.933_mnli_mismatched-0.608-0.925"
              ".9258981491734342")


@app.route('/', methods=["POST"])
def hello():
    body = request.get_json()
    prediction = model.predict(body['premise'], body['hypothesis'])
    return {"prediction": prediction}
