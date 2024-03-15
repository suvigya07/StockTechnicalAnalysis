# Import required libraries
from flask import Flask, render_template, request
import yfinance as yf
from ta.trend import SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.momentum import StochasticOscillator
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    symbol = request.form['symbol']
    prediction, bullishness_rating, bearishness_rating, sma_50, sma_200, rsi, macd, stochastic = make_prediction(symbol)
    suggestion = get_suggestion(prediction)
    return render_template('prediction.html', symbol=symbol, prediction=prediction, suggestion=suggestion,
                           bullishness_rating=bullishness_rating, bearishness_rating=bearishness_rating,
                           sma_50=sma_50, sma_200=sma_200, rsi=rsi, macd=macd, stochastic=stochastic)

def make_prediction(symbol):
    # Fetch historical stock data
    stock_data = yf.download(symbol, start='2021-01-01', end='2022-01-01')

    # Calculate moving averages
    sma_50 = SMAIndicator(close=stock_data['Close'], window=50).sma_indicator().iloc[-1]
    sma_200 = SMAIndicator(close=stock_data['Close'], window=200).sma_indicator().iloc[-1]

    # Calculate RSI
    rsi = RSIIndicator(close=stock_data['Close']).rsi().iloc[-1]

    # Calculate MACD
    macd = MACD(close=stock_data['Close']).macd().iloc[-1]

    # Calculate Stochastic Oscillator
    stochastic = StochasticOscillator(high=stock_data['High'], low=stock_data['Low'], close=stock_data['Close']).stoch().iloc[-1]

    # Calculate bullishness and bearishness ratings
    bullish_indicators = [sma_50 > sma_200, rsi > 50, macd > 0, stochastic > 50]
    bearish_indicators = [sma_50 < sma_200, rsi < 50, macd < 0, stochastic < 50]
    bullishness_rating = sum(bullish_indicators) * 10 / len(bullish_indicators)
    bearishness_rating = sum(bearish_indicators) * 10 / len(bearish_indicators)

    # Determine prediction based on bullishness rating
    if bullishness_rating >= 7:
        prediction = "Bullish"
    elif bullishness_rating >= 4:
        prediction = "Hold"
    else:
        prediction = "Bearish"

    return prediction, bullishness_rating, bearishness_rating, sma_50, sma_200, rsi, macd, stochastic

def get_suggestion(prediction):
    if prediction == "Bullish":
        suggestion = "Considering the positive indicators, it may be a good time to buy or hold the stock."
    elif prediction == "Hold":
        suggestion = "The stock may be in a stable state. Consider holding the stock if you already own it."
    else:
        suggestion = "Based on the indicators, it may be wise to consider selling or avoiding the stock."
    return suggestion

if __name__ == '__main__':
    app.run(debug=True)
