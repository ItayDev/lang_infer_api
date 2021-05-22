from typing import List
import ModelLoader
from data.NewsRequester import NewsRequester
from data.TweetsRequester import TweetsRequester, Tweet
from models.pattern import Parameters, DatasetPrepare, PatternModelAnalyzer
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
def run_pattern_model(texts):
    tokenized_titles = DatasetPrepare.encode_bert(texts)
    prediction_tensor = pattern_model(tokenized_titles)
    prediction_of_true_label = [pred_tensor[Parameters.TRUE_LABEL_INDEX] for pred_tensor in prediction_tensor.squeeze().tolist()]
    return {"predictions": prediction_of_true_label}


def pattern_model_grader(account_name, start_date=None, end_date=None):
    tweets = retrieve_tweets(account_name, start_date, end_date)
    texts = [tweet.clean_content for tweet in tweets]
    probabilities = run_pattern_model(texts)["predictions"]
    texts_with_probs = list(zip(tweets, probabilities))
    return {
        "significant_tweets": [tweet[0]
                               for tweet
                               in PatternModelAnalyzer.filter_significant_results(texts_with_probs)],
        "pattern_score": PatternModelAnalyzer.grade_account(texts_with_probs)
    }


# Retrieve news from news api
def evaluate_tweets_with_news(tweets: list[Tweet]):
    return tweets_evaluator.eval_tweets(tweets)


def retrieve_tweets(person, start_date: datetime = None, end_date: datetime= None):
    return tweets_requester.fetch_tweets_from_server(person, start_date, end_date)


def classify(account_name, start_date, end_date):
    tweets = retrieve_tweets(account_name, start_date, end_date)
    pattern_result = pattern_model_grader(tweets)
    significant_tweets = pattern_result["significant_tweets"]
    tweets_with_news = evaluate_tweets_with_news(significant_tweets)

    return {
        "score": pattern_result["pattern_score"],
        "relevantArticles": tweets_with_news
    }
