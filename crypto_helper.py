import time
import requests
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import math
import os

# Define API endpoint and parameters
url = 'https://api.binance.com/api/v3/ticker/24hr'

# Initialize plots
plt.ion()
fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=False)
fig.subplots_adjust(hspace=0.5)

# Initialize dictionary to cache prices
prices_cache = {}
total_cache = {}

grey = "#8C8C8C"
green = "#00FF00"
red = "#FF0000"
stablecoin = "USDT"
min_percent_change = 10
min_coin_value = 0.000001
num_biggest_changes = 20

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

def colorFader(c1,c2,mix=0):
    c1=np.array(mpl.colors.to_rgb(c1))
    c2=np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)

def get_color(value, _min = -5, _max = 5):
    if value > 0:
        color = colorFader(grey, green, min(value, _max) / _max)
    else:
        color = colorFader(grey, red, max(value, _min) / _min)
    return color

def plot_data(volatile, dynamics):

    plot_volatile(volatile, axs[0])
    plot_dynamics(dynamics, axs[1])

    # Rotate x-axis labels for readability
    for ax in axs.flat:
        plt.sca(ax)
        plt.xticks(rotation=45)

    plt.show()
    plt.pause(2)

def plot_volatile(coins, container):
    container.clear()

    # Add last price and percentage change to end of each bar
    for i, coin in enumerate(coins):

        # Set the color depending on the value of the change percent
        color = get_color(coin.change_percent)
        bar = container.bar(coin.name, coin.current_percent_change, color=color)

        # Add text to the top of the bar
        container.text(coin.name, coin.change_percent, "{:.1f}%".format(coin.change_percent), ha='center', va='bottom')
        container.text(i, bar[0].get_height() - 1 + int(math.copysign(2, coin.current_percent_change)), f"{coin.last_price:.3f}\n{coin.current_percent_change:.1f}%", ha='center', fontsize=8)

    
    # Set y-containeris limits
    container.set_ylim(min(coin.current_percent_change for coin in coins) - 5, max(coin.current_percent_change for coin in coins) + 5)
    container.set_title(f"most volatile - {stablecoin}")

def plot_dynamics(coins, container):
    container.clear()

    for i, coin in enumerate(coins):

        color = get_color(coin.change_percent)
        bar = container.bar(coin.name, coin.change_percent, color=color)
        container.text(coin.name, coin.change_percent, "{:.1f}%".format(coin.change_percent), ha='center', va='bottom')
        container.text(i, bar[0].get_height() - 1 + int(math.copysign(4, coin.change_percent)), f"{coin.last_price:.3f}", ha='center', fontsize=8)

    container.set_ylim(min(coin.current_percent_change for coin in coins) - 5, max(coin.current_percent_change for coin in coins) + 5)
    container.set_title(f"most dynamic - {stablecoin}")

while True:
    try:
        # Get data from API
        response = requests.get(url)
        data = response.json()

        filtered_data = [coin for coin in data if (float(coin['priceChangePercent']) < -min_percent_change or float(coin['priceChangePercent']) > min_percent_change) and stablecoin in coin['symbol']]
        sorted_data = sorted(filtered_data, key=lambda p: p['priceChangePercent'])
        data_without_small_coins = [coin for coin in data if float(coin['lastPrice']) > min_coin_value and stablecoin in coin['symbol']]

        update_cache(prices_cache, sorted_data)
        update_cache(total_cache, data_without_small_coins)

        os.system('clear')
        sorted_total_cache = sorted(total_cache.values(), key=lambda x: abs(x.change_percent), reverse=True)
        sorted_total_cache = sorted(sorted_total_cache[:num_biggest_changes], key=lambda x: x.change_percent, reverse=True)
        for coin in sorted_total_cache:
            print(f"{coin.name}: {coin.last_price} ({round(coin.change_percent, 1)}%)")

        sorted_prices_cache = sorted(prices_cache.values(), key=lambda x: (x.current_percent_change > 0, abs(x.current_percent_change)), reverse=True)
        plot_data(sorted_prices_cache, sorted_total_cache)
        time.sleep(1)

    except Exception as e:
        print(f"Error occurred: {e}")