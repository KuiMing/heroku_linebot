import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,
                            FlexSendMessage)
import json

app = Flask(__name__)
LINE_SECRET = os.getenv('LINE_SECRET')
LINE_TOKEN = os.getenv('LINE_TOKEN')
LINE_BOT = LineBotApi(LINE_TOKEN)
HANDLER = WebhookHandler(LINE_SECRET)


@app.route("/")
def hello():
    "hello world"
    return "Hello World!!!!!"


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


@HANDLER.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """
    Reply text message
    """
    with open("bubble.json", "r") as f_h:
        bubble = json.load(f_h)
    f_h.close()
    text = event.message.text.replace(" ", "").lower()
    if text == "github":
        output = "https://github.com/KuiMing/heroku_linebot"
        message = TextSendMessage(text=output)
    elif text == "currency":
        bubble = bubble['contents'][0]
        message = FlexSendMessage(alt_text="Report", contents=bubble)
    else:
        output = text
        message = TextSendMessage(text=output)
    LINE_BOT.reply_message(event.reply_token, message)


if __name__ == "__main__":
    app.run(debug=True)
