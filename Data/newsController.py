import requests


def getNews(hypothesis):
    headlines = []
    key = "mkmf1ZFfJzxR1gmt2GUW0JppZXKDHg9M"
    url = "https://api.nytimes.com/svc/search/v2/articlesearch.json?q=" + hypothesis + "&api-key=" + key
    result = requests.get(url)

    articles = (result.json())["response"]["docs"]
    for art in articles:
        headlines.append(art['headline']['main'])

    for premise in headlines:
        print(premise)
        # perdict =  model.predict(premise, hypothesis) //TODO once the model will be loaded
        # perdict // TODO average the prediction and send a percentage

    percentage = 0
    return str(percentage)
