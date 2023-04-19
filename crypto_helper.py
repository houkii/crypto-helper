import time
import requests
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import math
import os

# Define API endpoint and parameters
url = 'https://api.binance.com/api/v3/ticker/24hr'

# Set interactive mode on
plt.ion()

# Initialize plot
fig, ax = plt.subplots()
ax.set_xlabel('Name')
ax.set_ylabel('Price change (1h)')

# Initialize dictionary to cache prices
prices_cache = {}
total_cache = {}

grey = "#8C8C8C"
green = "#00FF00"
red = "#FF0000"

stablecoin = "USDT"

class Coin:
    def __init__(self, name, last_price, change, start_price=None):
        self.name = name
        self.last_price = last_price
        self.start_price = start_price or last_price
        self.change_percent = 0
        self.startup_percent_change = change
        self.current_percent_change = change
        
    def update_price(self, new_price, percent_change):
        
        self.last_price = new_price
        self.current_percent_change = percent_change
        self.change_percent =  (1 - (self.start_price / new_price)) * 100

def update_cache(cache, data, print_=False):
    for coin in data:
        name, last_price, price_change = coin['symbol'], float(coin['lastPrice']), float(coin['priceChangePercent'])
        if print_:
            print(f"Name: {name}\nCurrent price: {last_price}\nPrice change: {price_change}%")
        
        coin_obj = Coin(name.replace(stablecoin, ""), last_price, price_change)
        
        if name not in cache:
            cache[name] = coin_obj;
        else:
            cache[name].update_price(last_price, price_change)
        
        if print_:
            print(f"start_price: {coin_obj.start_price}\ndiff since start: {coin_obj.change_percent}%\n")

def colorFader(c1,c2,mix=0): #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
    c1=np.array(mpl.colors.to_rgb(c1))
    c2=np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)

def plot_data(coins):

    ax.clear()

    # Add last price and percentage change to end of each bar
    for i, coin in enumerate(coins):

        # Set the color depending on the value of the change percent
        if coin.change_percent > 0:
            color = colorFader(grey, green, min(coin.change_percent, 5) / 5)
        else:
            color = colorFader(grey, red, max(coin.change_percent, -5) / -5)

        bar = ax.bar(coin.name, coin.current_percent_change, color=color)

        # Add text to the top of the bar
        ax.text(coin.name, coin.change_percent, "{:.1f}%".format(coin.change_percent), ha='center', va='bottom')
        ax.text(i, bar[0].get_height() - 1 + int(math.copysign(2, coin.current_percent_change)), f"{coin.last_price:.4f}\n{coin.current_percent_change:.1f}%", ha='center', fontsize=8)

    # Set y-axis limits
    ax.set_ylim(min(coin.current_percent_change for coin in coins) - 5, max(coin.current_percent_change for coin in coins) + 5)
    ax.set_title(stablecoin);

    # Rotate x-axis labels for readability
    plt.xticks(rotation=90)
    plt.show()
    plt.pause(2)

while True:
    try:
        # Get data from API
        response = requests.get(url)
        data = response.json()

        filtered_data = [coin for coin in data if (float(coin['priceChangePercent']) < -10 or float(coin['priceChangePercent']) > 10) and stablecoin in coin['symbol']]
        sorted_data = sorted(filtered_data, key=lambda p: p['priceChangePercent'])

        data_without_small_coins = [coin for coin in data if float(coin['lastPrice']) > 0.000001 and stablecoin in coin['symbol']]

        update_cache(prices_cache, sorted_data)
        update_cache(total_cache, data_without_small_coins)

        os.system('clear')
        sorted_total_cache = sorted(total_cache.values(), key=lambda x: abs(x.change_percent), reverse=True)
        sorted_total_cache = sorted(sorted_total_cache[:20], key=lambda x: x.change_percent, reverse=True)
        for coin in sorted_total_cache:
            print(f"{coin.name}: {coin.last_price} ({round(coin.change_percent, 1)}%)")

        sorted_prices_cache = sorted(prices_cache.values(), key=lambda x: (x.current_percent_change > 0, abs(x.current_percent_change)), reverse=True)
        plot_data(sorted_prices_cache)
        time.sleep(1)

    except Exception as e:
        print(f"Error occurred: {e}")