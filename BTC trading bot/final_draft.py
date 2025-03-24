import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def load_data(file_path):
    data = pd.read_csv(file_path)
    data['datetime'] = pd.to_datetime(data['datetime'])
    data.set_index('datetime', inplace=True)
    return data

def moving_average_crossover(data, short_window, long_window, output_file):
    data['Short_MA'] = data['close'].rolling(window=short_window).mean()
    data['Long_MA'] = data['close'].rolling(window=long_window).mean()
    data['Signal'] = 0
    data.loc[data['Short_MA'] > data['Long_MA'], 'Signal'] = 1
    data.loc[data['Short_MA'] < data['Long_MA'], 'Signal'] = -1

    signal_data = data[['close', 'Short_MA', 'Long_MA', 'Signal']]
    signal_data.to_csv(output_file)

    return data

def backtest_strategy(data, initial_capital=10000):
    data['Daily_Return'] = data['close'].pct_change().fillna(0)
    data['Strategy_Return'] = data['Signal'].shift(1) * data['Daily_Return']
    data['Strategy_Return'] = data['Strategy_Return'].fillna(0)

    # Calculate cumulative returns in percentage and dollars
    data['Cumulative_Strategy'] = (1 + data['Strategy_Return']).cumprod()
    data['Cumulative_BuyHold'] = (1 + data['Daily_Return']).cumprod()
    data['Strategy_Profit'] = initial_capital * data['Cumulative_Strategy']
    data['BuyHold_Profit'] = initial_capital * data['Cumulative_BuyHold']
    return data

def calculate_sharpe_ratio(data, risk_free_rate=0.02):
    excess_returns = data['Strategy_Return'] - (risk_free_rate / 252)
    sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    return sharpe_ratio

def calculate_trade_statistics(data):
    trades = data[data['Signal'] != 0]  # Only consider rows where a trade occurred
    total_trades = len(trades)
    trades['Profit'] = trades['Strategy_Return'] * trades['close']
    winning_trades = trades[trades['Profit'] > 0]
    losing_trades = trades[trades['Profit'] < 0]

    gross_profit = winning_trades['Profit'].sum()
    net_profit = trades['Profit'].sum()
    largest_win = winning_trades['Profit'].max() if not winning_trades.empty else 0
    smallest_win = winning_trades['Profit'].min() if not winning_trades.empty else 0
    largest_loss = losing_trades['Profit'].min() if not losing_trades.empty else 0
    max_drawdown = (data['Strategy_Profit'].cummax() - data['Strategy_Profit']).max()

    long_trades = len(trades[trades['Signal'] == 1])
    short_trades = len(trades[trades['Signal'] == -1])
    win_percentage = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0

    return {
        'Total Trades': total_trades,
        'Winning Trades': len(winning_trades),
        'Losing Trades': len(losing_trades),
        'Gross Profit': gross_profit,
        'Net Profit': net_profit,
        'Largest Win': largest_win,
        'Smallest Win': smallest_win,
        'Largest Loss': largest_loss,
        'Max Drawdown': max_drawdown,
        'Long Trades': long_trades,
        'Short Trades': short_trades,
        'Win Percentage': win_percentage
    }

def visualize_results(data):
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(data.index, data['close'], label='Close Price', color='black')
    plt.plot(data.index, data['Short_MA'], label='Short MA', color='blue', linestyle='--')
    plt.plot(data.index, data['Long_MA'], label='Long MA', color='orange', linestyle='--')
    plt.title('Bitcoin Price with Moving Averages')
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(data.index, data['Strategy_Profit'], label='Strategy Profit ($)', color='green')
    plt.plot(data.index, data['BuyHold_Profit'], label='Buy & Hold Profit ($)', color='red')
    plt.title('Cumulative Profits')
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    file_path = "BTC_Data _(2019-2023)\\BTC_2019_2023_1w.csv"  # Replace with the path to your CSV file
    output_file = "signals.csv"

    short_window = 5
    long_window = 50
    initial_capital = 10000  # in dollars

    data = load_data(file_path)
    data = moving_average_crossover(data, short_window, long_window, output_file)
    data = backtest_strategy(data, initial_capital=initial_capital)

    sharpe_ratio = calculate_sharpe_ratio(data)
    trade_stats = calculate_trade_statistics(data)

    print(f"Final Strategy Cumulative Profit: ${data['Strategy_Profit'].iloc[-1]:.2f}")
    print(f"Final Buy & Hold Cumulative Profit: ${data['BuyHold_Profit'].iloc[-1]:.2f}")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    print("Trade Statistics:")
    for key, value in trade_stats.items():
        print(f"{key}: {value}")

    visualize_results(data)
