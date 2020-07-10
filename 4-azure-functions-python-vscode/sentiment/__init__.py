import azure.functions as func
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def main(req: func.HttpRequest) -> func.HttpResponse:
    analyzer = SentimentIntensityAnalyzer()
    text = req.params.get("text")
    if text is None:
        return func.HttpResponse(status_code=302, headers={"Location":req.url+"?text=I+Love+PyCon"})
    scores = analyzer.polarity_scores(text)
    sentiment = "positive" if scores["compound"] > 0 else "negative"
    return func.HttpResponse(sentiment)
    
