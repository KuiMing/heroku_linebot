"""
Line Chatbot tutorial
"""
from flask import Flask

APP = Flask(__name__)


@APP.route("/")
def hello() -> str:
    "hello world"
    return "Hello World!!!!!"


if __name__ == "__main__":
    APP.run(debug=True)
