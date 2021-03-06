MIN_TRUE_THRESHOLD = 0.5
MAX_FALSE_THRESHOLD = 0.15

"""
This function is intended to filter out any indefinite results, whose probability to 
be false or true are not that high. 
The default thresholds are configured above. 

:param results_with_probs 
    a list containing pairs of texts and their probabilities to be truthful, 
    possibly constructed by zip of the texts and probabilities such as:
    (("Trump is lying", 0.9), ("I like pasta", 0.6), ("peace in the middle east", 0.1))
    
:return a list that has only definite probabilities of either true or false
"""
def filter_significant_results(results_with_probs,
                               lower_threshold=MIN_TRUE_THRESHOLD,
                               upper_threshold=MAX_FALSE_THRESHOLD):
    filter_unwanted_items = \
        filter(lambda item: filter_result(item, lower_threshold, upper_threshold), results_with_probs)

    return list(filter_unwanted_items)


def filter_result(result, min_true_threshold, max_false_threshold):
    probability = result[1]
    return (probability >= min_true_threshold) or (probability <= max_false_threshold)


"""
This function is intended to grade account based on probabilities of its texts. 
The default probabilities for true or misleading texts are configured above.

:param results_with_probs 
    a list containing pairs of texts and their probabilities to be truthful, 
    possibly constructed by zip of the texts and probabilities such as:
    (("Trump is lying", 0.9), ("I like pasta", 0.6), ("peace in the middle east", 0.1))
    
:return a grade in the range of [-1, 1] indication how truthful are the texts of the account,
when -1 indicating complete liar while 1 indicting the most honest person
"""
def grade_account(results_with_probs,
                  lower_threshold=MIN_TRUE_THRESHOLD,
                  upper_threshold=MAX_FALSE_THRESHOLD):

    true_texts_count = sum(1
                           for text_with_prob in results_with_probs
                           if text_with_prob[1] > lower_threshold)
    false_texts_count = sum(1
                            for text_with_prob in results_with_probs
                            if text_with_prob[1] < upper_threshold)

    total_tweets = false_texts_count + true_texts_count

    if total_tweets == 0:
        return 0

    true_tweet_ratio = true_texts_count / total_tweets
    return 2 * true_tweet_ratio - 1
