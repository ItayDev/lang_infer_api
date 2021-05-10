import ModelLoader
from Data import newsController
from Models.Pattern import Parameters, DatasetPrepare, SignificantResultsFilter

hypothesis_model = ModelLoader.load_hypothesis_model()
pattern_model = ModelLoader.load_pattern_model()


# Run the hypothesis model over pairs of hypothesis and premise,
# and return the probability of each of each hypothesis to be inferred from premise
def run_hypothesis_model(body):
    prediction = hypothesis_model.predict(body)
    return {"predictions": prediction}


# Run the pattern model over the given list of titles,
# and return the probability for truth per each title
def run_pattern_model(body):
    titles = body['titles']
    tokenized_titles = DatasetPrepare.encode_bert(titles)
    prediction_tensor = pattern_model(tokenized_titles)
    prediction_of_true_label = [pred_tensor[Parameters.TRUE_LABEL_INDEX] for pred_tensor in prediction_tensor.squeeze().tolist()]
    return {"predictions": prediction_of_true_label}


def pattern_model_filter(body):
    texts = body['titles']
    probabilities = run_pattern_model(body)["predictions"]
    return {"predictions": SignificantResultsFilter.filter_significant_results(zip(texts, probabilities))}


# Retrieve news from news api
def fetch_news(hypothesis):
    return newsController.getNews(hypothesis)

