import os
import json
from datetime import datetime, timedelta
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    FlexSendMessage,
)
from keras.models import load_model
import investpy
import pickle

app = Flask(__name__)
LINE_SECRET = os.getenv('LINE_SECRET')
LINE_TOKEN = os.getenv('LINE_TOKEN')
LINE_BOT = LineBotApi(LINE_TOKEN)
HANDLER = WebhookHandler(LINE_SECRET)


@app.route("/")
def hello():
    "hello world"
    return "Hello World!!!!!"


@app.route("/predict")
def predict():
    """
    Prediction
    """
    today = datetime.now()
    model = load_model("model.h5")
    with open("scaler.pickle", "rb") as f_h:
        scaler = pickle.load(f_h)
    f_h.close()
    data = investpy.get_currency_cross_historical_data(
        "USD/TWD",
        from_date=(today - timedelta(weeks=105)).strftime("%d/%m/%Y"),
        to_date=today.strftime("%d/%m/%Y"),
    )
    data.reset_index(inplace=True)
    data = data.tail(240).Close.values.reshape(-1, 1)
    data = scaler.transform(data)
    data = data.reshape((1, 240, 1))
    # make prediction
    ans = model.predict(data)
    ans = scaler.inverse_transform(ans)
    return str(round(ans[0][0], 2))


@app.route("/callback", methods=["POST"])
def callback():
    """
    LINE bot webhook callback
    """
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]
    print(signature)
    body = request.get_data(as_text=True)
    print(body)
    try:
        HANDLER.handle(body, signature)
    except InvalidSignatureError:
        print(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        abort(400)
    return "OK"


def bubble_currency():
    """
    create currency bubble
    """
    with open("bubble.json", "r") as f_h:
        bubble = json.load(f_h)
    f_h.close()
    bubble = bubble['contents'][0]
    recent = investpy.get_currency_cross_recent_data("USD/TWD")
    bubble['body']['contents'][1]['contents'][0]['contents'][0]['text'] = \
        f"{round(recent.Close.values[-1], 2)} TWD = 1 USD"
    return bubble


def bubble_predcition():
    """
    create prediction bubble
    """
    with open("bubble.json", "r") as f_h:
        bubble = json.load(f_h)
    f_h.close()
    bubble_pred = bubble['contents'][1]
    predicted_currency = predict()
    bubble_pred['body']['contents'][1]['contents'][0]['contents'][0]['text'] = \
        f"{predicted_currency} TWD = 1 USD"
    bubble_curr = bubble_currency()
    bubble['contents'][0] = bubble_curr
    bubble['contents'][1] = bubble_pred
    return bubble


@HANDLER.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """
    Reply text message
    """
    print(type(event))
    currency_option = dict(currency=bubble_currency,
                           prediction=bubble_predcition)
    text = event.message.text.replace(" ", "").lower()
    if text == "github":
        output = "https://github.com/KuiMing/heroku_linebot"
        message = TextSendMessage(text=output)
    elif text in currency_option.keys():
        bubble = currency_option[text]()
        message = FlexSendMessage(alt_text="Report", contents=bubble)
    else:
        output = text
        message = TextSendMessage(text=str(type(event)))
    LINE_BOT.reply_message(event.reply_token, message)


if __name__ == "__main__":
    app.run(debug=True)
