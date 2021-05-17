import ModelLoader
from data.NewsRequester import NewsRequester
from data.TweetsRequester import TweetsRequester, clean_tweet
from models.pattern import Parameters, DatasetPrepare, SignificantResultsFilter
from models.inference.TweetsEvaluator import TweetsEvaluator
from datetime import datetime

inference_model = ModelLoader.load_inference_model()
pattern_model = ModelLoader.load_pattern_model()
news_requester = NewsRequester()
tweets_evaluator = TweetsEvaluator(inference_model, news_requester)
tweets_requester = TweetsRequester()

# TODO: This method should get as an input tweets and not the body directly
# Run the pattern model over the given list of titles,
# and return the probability for truth per each title
def run_pattern_model(body):
    titles = body['titles']
    tokenized_titles = DatasetPrepare.encode_bert(titles)
    prediction_tensor = pattern_model(tokenized_titles)
    prediction_of_true_label = [pred_tensor[Parameters.TRUE_LABEL_INDEX] for pred_tensor in prediction_tensor.squeeze().tolist()]
    return {"predictions": prediction_of_true_label}


# TODO: This method should get as an input tweets and not the body directly.
#  it should filter those tweets and return them
def pattern_model_filter(body):
    texts = body['titles']
    probabilities = run_pattern_model(body)["predictions"]
    return {"predictions": SignificantResultsFilter.filter_significant_results(zip(texts, probabilities))}


# Retrieve news from news api
def evaluate_tweets_with_news(tweets):
    return tweets_evaluator.eval_tweets(tweets)


def retrieve_tweets(person, start_date: datetime = None, end_date: datetime=None):
    tweets = tweets_requester.fetch_tweets_from_server(person, start_date, end_date)
    return [clean_tweet(tweet.full_text) for tweet in tweets]
