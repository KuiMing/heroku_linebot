"""
Line Chatbot tutorial
"""
from datetime import datetime, timedelta
import pickle
from flask import Flask
from keras.models import load_model
import investpy

APP = Flask(__name__)


@APP.route("/")
def hello() -> str:
    "hello world"
    return "Hello World!!!!!"


@APP.route("/predict")
def predict() -> str:
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


if __name__ == "__main__":
    APP.run(debug=True)
