"""
Line Chatbot tutorial
"""
import os
import json
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    FlexSendMessage,
)
import investpy

APP = Flask(__name__)
LINE_SECRET = os.getenv('LINE_SECRET')
LINE_TOKEN = os.getenv('LINE_TOKEN')
LINE_BOT = LineBotApi(LINE_TOKEN)
HANDLER = WebhookHandler(LINE_SECRET)


@APP.route("/")
def hello() -> str:
    "hello world"
    return "Hello World!!!!!"


@APP.route("/callback", methods=["POST"])
def callback() -> str:
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


def bubble_currency() -> dict:
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


@HANDLER.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent) -> None:
    """
    Reply text message
    """
    text = event.message.text.replace(" ", "").lower()
    if text == "currency":
        bubble = bubble_currency()
        message = FlexSendMessage(alt_text="Report", contents=bubble)
        LINE_BOT.reply_message(event.reply_token, message)
    if text == "github":
        output = "https://github.com/KuiMing/heroku_linebot"
    else:
        output = text
    message = TextSendMessage(text=output)
    LINE_BOT.reply_message(event.reply_token, message)


if __name__ == "__main__":
    APP.run(debug=True)
