import time
import requests
import matplotlib.pyplot as plt
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

class Coin:
    def __init__(self, symbol, last_price, price_change_percent):
        self.symbol = symbol
        self.last_price = last_price
        self.price_change_percent = price_change_percent

    def __repr__(self):
        return f"Coin({self.symbol}, {self.last_price}, {self.price_change_percent})"

def get_coins(data):
    coins = []
    for coin in data:
        symbol = coin['symbol']
        last_price = float(coin['lastPrice'])
        price_change_percent = float(coin['priceChangePercent'])
        coins.append(Coin(symbol, last_price, price_change_percent))

    return coins

def update_cache(cache, data, print=False):
    # Print data for each coin
    for coin in data:
        name = coin['symbol']
        price_change = coin['priceChangePercent']
        last_price = coin['lastPrice']
        if print:
            print(f"Name: {name}")
            print(f"Current price: {last_price}")
            print(f"Price change: {price_change}%")
        
        if name not in cache:
            cache[name] = {'start_price': last_price, 'change_percent': 0}
        else:
            start_price = cache[name]['start_price']
            change = 1 - (float(start_price) / float(last_price))
            cache[name]['change_percent'] = change * 100
            formatted_change = "{:.3f}".format(change)
            if print:
                print(f"start_price: {start_price}")
                print(f"diff since start: {formatted_change}%\n")    


while True:
    try:
        # Get data from API
        response = requests.get(url)
        data = response.json()


        coins = get_coins(data)
        usdt_coins = [coin for coin in coins if "usdt" in coin.symbol.lower()]

        print(usdt_coins)

        filtered_data = [coin for coin in data if (float(coin['priceChangePercent']) < -10 or float(coin['priceChangePercent']) > 10) and "usdt" in coin['symbol'].lower()]
        sorted_data = sorted(filtered_data, key=lambda p: p['priceChangePercent'])

        data_without_small_coins = [coin for coin in data if float(coin['lastPrice']) > 0.000001 and "usdt" in coin['symbol'].lower()]

        update_cache(prices_cache, sorted_data)
        update_cache(total_cache, data_without_small_coins)

        os.system('clear')
        sorted_total_cache = sorted(total_cache.items(), key=lambda x: abs(x[1]['change_percent']), reverse=True)
        for entry in sorted_total_cache[:20]:
            print(entry)

        # Extract coin names and price change percentage for plotting
        names = [coin['symbol'] for coin in sorted_data]
        changes = [float(coin['priceChangePercent']) for coin in sorted_data]
        prices = [float(coin['lastPrice']) for coin in sorted_data]
        diff_start = [prices_cache[name]['change_percent'] for name in names]

        # Clear previous plot and create new one
        ax.clear()
        # bars = ax.bar(names, changes)

        bars = []
        # Add last price and percentage change to end of each bar
        for i, change in enumerate(changes):
            color = 'r'
            if diff_start[i] > 0:
                color = 'g'

            bar = ax.bar(names[i], change, color=color)

            # Add text to the top of the bar
            ax.text(names[i], diff_start[i], "{:.1f}%".format(diff_start[i]), ha='center', va='bottom')

            ax.text(i, bar[0].get_height() + 1, f"{prices[i]:.4f}\n{changes[i]:.1f}%", ha='center', fontsize=8)

        # Set y-axis limits
        ax.set_ylim(min(changes) - 5, max(changes) + 5)

        # Rotate x-axis labels for readability
        plt.xticks(rotation=90)

        # Show plot
        plt.show()

        plt.pause(3)
        time.sleep(1)

    except Exception as e:
        print(f"Error occurred: {e}")