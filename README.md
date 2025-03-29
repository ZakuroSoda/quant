## Strategy:
1. Long: enter at below 35 rsi, exit at above 70
2. Short: enter at above 70, exit at 80% of entry RSI

## Metrics:
- *Equity Final (total/annualised): abs/perc*
Final equity is the final value of the portfolio at the end of the backtest. Annualised equity is the final equity value divided by the number of years the backtest ran for. The percentage value will show the total percentage returns of the strategy.

- *Equity Peak: abs/perc*
The peak equity is the highest value the portfolio reached during the backtest. The percentage value will show the highest percentage returns of the strategy.

- *Equity Low: abs/perc*
The low equity is the lowest value the portfolio reached during the backtest. The percentage value will show the lowest percentage returns of the strategy.

- *Volatility (annualised): perc*
Volatility is the standard deviation of the daily returns of the strategy (i.e. the changes in portfolio value daily, in percentage terms). The annualised volatility is the volatility value multiplied by the square root of the number of trading days in a year.

- *Buy & Hold Return (total/annualised): abs/perc*
The buy and hold return is the total return of the asset over the backtest period. The annualised buy and hold return is the total buy and hold return divided by the number of years the backtest ran for.

- *Sharpe Ratio*
We shall ignore the risk-free rate for this calculation. The Sharpe ratio is the ratio of the strategy’s annualised return to its annualised volatility.

- *P/L per Trade / Avg Return per Trade / Expected Value*
The profit or loss per trade is the average profit or loss of each trade taken by the strategy.

- *Winrate / Loss Rate*
Self-explanatory. The win rate is the percentage of trades that were profitable, while the loss rate is the percentage of trades that were unprofitable.

- *Average Time in Trade*

## Graphs:
- *Equity Curve*
The equity curve is a graph showing the value of the portfolio over time.

- *Asset Curve with Annotated Entry/Exit*
This is a graph of the asset’s price over time, with the strategy’s buy and sell points marked on the graph.

- *Discretised Distribution curve of returns*
This is a histogram of the strategy’s returns, showing the frequency of different return values. If there is a long left tail, it means that the strategy has a high risk of losing a lot of money in a single trade. If there is a long right tail, it means that the strategy has a high chance of making a lot of money in a single trade.