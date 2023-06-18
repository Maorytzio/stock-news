from dotenv import load_dotenv

import os
import requests
from twilio.rest import Client

load_dotenv()

STOCK_NAME = "PLUG"
COMPANY_NAME = "Plug Power Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

STOCK_API_KEY = os.getenv("STOCK_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

params = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY,
}
response = requests.get(url=STOCK_ENDPOINT, params=params)

data = response.json()["Time Series (Daily)"]
data_list = [v for (k, v) in data.items()]

yday_close_price = float(data_list[0]["4. close"])
yyday_close_price = float(data_list[1]["4. close"])

delta = yday_close_price - yyday_close_price

up_down = None
if delta > 0:
    up_down = "💹"
else:
    up_down = "🔻"

delta_percent = round((delta / yday_close_price) * 100, 1)
print(delta_percent)

if abs(delta_percent) > 1:
    print("Get News")
    news_params = {
        "apiKey": NEWS_API_KEY,
        "q": COMPANY_NAME,
        "searchIn": "title"
    }
    news_response = requests.get(NEWS_ENDPOINT, news_params)
    articles = news_response.json()["articles"]
    three_articles = articles[:3]
    print(three_articles)

    article_list = [f"Headline: {article['title']}.\nBrief: {article['description']}"
                    for article in three_articles]

    ACCOUNT_SID = os.getenv("TWILIO_SID")
    AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
    PHONE_NUMBER = os.getenv("MY_PHONE_NUM")
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    for article in article_list:
        message = client.messages.create(
            body=f"{STOCK_NAME} {up_down} {delta_percent}%\n" + article,
            from_="+14066167599",
            to=PHONE_NUMBER
        )
        print(message.status)

