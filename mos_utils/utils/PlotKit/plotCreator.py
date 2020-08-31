import matplotlib.pyplot as plt



class PlotFinanceGraphs:
    def __init__(self):



plt.plot(prices_range, option_price6m, label="6m to maturity")
plt.plot(prices_range, option_price3m, label="3m to maturity")
plt.plot(prices_range, option_price10d, label="10d to maturity")
plt.xlabel("Spot Price")
plt.ylabel("Option Price")
plt.title("Relation price option to maturity")
plt.legend()
plt.savefig('OptionPrice.png')