
MIN_TRUE_THRESHOLD = 0.85
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
                               min_true_threshold=MIN_TRUE_THRESHOLD,
                               max_false_threshold=MAX_FALSE_THRESHOLD):

    return []









