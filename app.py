from flask import Flask, request, jsonify, json
from model.predict import Model

app = Flask(__name__)

model = Model("saved_models/1042176_snli-0.8-0.747_mnli_matched-0.65-0.891_mnli_mismatched-0.655-0.888")


@app.route('/', methods=["POST"])
def hello():
    body = request.get_json()
    prediction = model.predict(body)
    return {"predictions": prediction}
