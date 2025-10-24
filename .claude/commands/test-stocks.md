---
description: Run a quick test of the stock fetcher to verify stocks are accessible
---

Please test the stock fetching functionality:

1. Run the stock fetcher to get current prices for all stocks in config/stocks.json
2. Display the current prices
3. Check if there are any errors
4. Verify the stock symbols are valid

Use: `python -c "from src.stock_fetcher import StockFetcher; import json; f = StockFetcher(); stocks = json.load(open('config/stocks.json')); symbols = [s['symbol'] for s in stocks['stocks']]; print(f.get_multiple_prices(symbols))"`
