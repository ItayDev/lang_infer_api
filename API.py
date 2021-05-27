from typing import List
import ModelLoader
from data.NewsRequester import NewsRequester
from data.TweetsRequester import TweetsRequester, Tweet
from models.pattern import Parameters, DatasetPrepare, PatternModelAnalyzer
from models.inference.TweetsEvaluator import TweetsEvaluator


class API:
    def __init__(self):
        self.inference_model = ModelLoader.load_inference_model()
        self.pattern_model = ModelLoader.load_pattern_model()
        self.news_requester = NewsRequester()
        self.tweets_evaluator = TweetsEvaluator(self.inference_model, self.news_requester)
        self.tweets_requester = TweetsRequester()

    def run_pattern_model(self, texts):
        tokenized_titles = DatasetPrepare.encode_bert(texts)
        prediction_tensor = self.pattern_model(tokenized_titles)
        prediction_of_true_label = [pred_tensor[Parameters.TRUE_LABEL_INDEX] for pred_tensor in prediction_tensor.tolist()]
        return {"predictions": prediction_of_true_label}

    def pattern_model_grader(self, tweets):
        texts = [tweet.clean_content for tweet in tweets]
        probabilities = self.run_pattern_model(texts)["predictions"]
        texts_with_probs = list(zip(tweets, probabilities))
        return {
            "significant_tweets": [tweet[0]
                                   for tweet
                                   in PatternModelAnalyzer.filter_significant_results(texts_with_probs)],
            "pattern_score": PatternModelAnalyzer.grade_account(texts_with_probs)
        }

    # Retrieve news from news api
    def evaluate_tweets_with_news(self, tweets: List[Tweet]):
        return self.tweets_evaluator.eval_tweets(tweets)

    def retrieve_tweets(self, person):
        return self.tweets_requester.fetch_tweets_from_server(person)

    def classify(self, account_name):
        tweets = self.retrieve_tweets(account_name)
        pattern_result = self.pattern_model_grader(tweets)
        significant_tweets = pattern_result["significant_tweets"]
        tweets_with_news = self.evaluate_tweets_with_news(significant_tweets)

        return {
            "score": pattern_result["pattern_score"],
            "relevantArticles": tweets_with_news
        }
