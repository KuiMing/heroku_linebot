from flask import Flask, request, abort

app = Flask(__name__)


@app.route("/")
def hello():
    "hello world"
    return "Hello World!!!!!"


if __name__ == "__main__":
    app.run(debug=True)
