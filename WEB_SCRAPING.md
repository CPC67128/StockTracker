# Web Scraping Guide

## Overview

StockTracker now supports **web scraping** as an alternative to the Yahoo Finance API. This feature helps you avoid API rate limiting issues by fetching stock prices directly from financial websites.

## Why Use Web Scraping?

### Problems with Yahoo Finance API:
- ❌ Strict rate limits (429 errors)
- ❌ Frequent temporary blocks
- ❌ Unreliable for frequent checks
- ❌ No official API (relies on unofficial library)

### Benefits of Web Scraping:
- ✅ **No API rate limits**
- ✅ Multiple data sources (Google Finance, MarketWatch, Boursorama)
- ✅ Automatic fallback between sources
- ✅ More reliable for production use
- ✅ Works even when Yahoo Finance is down

## Supported Data Sources

The web scraper tries multiple sources in order:

1. **Google Finance** - Fast, reliable (though selectors may change)
2. **MarketWatch** - Very reliable, good uptime
3. **Boursorama** - French financial site (good for European stocks)

## How to Enable Web Scraping

### Method 1: Environment Variable (Recommended)

Edit your `.env` file:

```env
USE_WEB_SCRAPING=true
```

That's it! The application will automatically use web scraping instead of the API.

### Method 2: Programmatic

```python
from stock_fetcher import StockFetcher

# Enable web scraping
fetcher = StockFetcher(use_web_scraping=True)
price = fetcher.get_stock_price('AAPL')
```

## Testing Web Scraping

### Test a Single Stock

```bash
python -c "import sys; sys.path.insert(0, 'src'); from web_scraper import WebScraper; scraper = WebScraper(); print(scraper.get_stock_price('AAPL'))"
```

### Test Specific Sources

```python
from web_scraper import WebScraper

scraper = WebScraper()

# Test MarketWatch only
price = scraper.get_stock_price('AAPL', sources=['marketwatch'])
print(f"AAPL: ${price}")

# Test Google Finance only
price = scraper.get_stock_price('GOOGL', sources=['google'])
print(f"GOOGL: ${price}")

# Test Boursorama (for European stocks)
price = scraper.get_stock_price('MC', sources=['boursorama'])  # LVMH
print(f"MC: ${price}")
```

## Stock Symbol Formats

Different sources may require different formats:

### US Stocks (NASDAQ, NYSE)
- **MarketWatch**: Use standard symbol (e.g., `AAPL`, `MSFT`)
- **Google Finance**: Auto-converts to `SYMBOL:NASDAQ` (e.g., `AAPL:NASDAQ`)
- **Boursorama**: Uses format `1rPSYMBOL` (e.g., `1rPAAPL`)

### European Stocks
- **Boursorama**: Best for French/European stocks
- Use local ticker symbols (e.g., `MC` for LVMH, `OR` for L'Oréal)

## How It Works

### Price Extraction Process

1. **HTTP Request**: Fetches the stock page HTML
2. **HTML Parsing**: Uses BeautifulSoup to parse the page
3. **Price Extraction**:
   - Tries multiple CSS selectors (sites change layouts)
   - Handles various price formats (USD, EUR, with/without symbols)
   - Supports both US (.) and European (,) decimal separators
4. **Fallback**: If one source fails, automatically tries the next

### Smart Price Parsing

The scraper can handle multiple price formats:
- `$259.60` (US format with dollar sign)
- `259.60 USD` (price with currency code)
- `259,60 €` (European format with comma)
- `1,234.56` (prices with thousands separator)
- `1.234,56` (European thousands separator)

## Configuration

### Default Sources Order

The scraper tries sources in this order:
1. Google Finance (fastest)
2. MarketWatch (most reliable)
3. Boursorama (for European stocks)

### Customizing Source Order

Edit `src/web_scraper.py` and modify the default sources:

```python
def get_stock_price(self, symbol: str, sources: list = None) -> Optional[float]:
    if sources is None:
        sources = ['marketwatch', 'google', 'boursorama']  # Your custom order
```

## Troubleshooting

### No Price Found

**Symptoms:**
```
WARNING:web_scraper:Could not find price element for AAPL
```

**Solutions:**
1. The website may have changed its HTML structure
2. Try a different source
3. Check if the symbol is correct for that source
4. Some stocks may not be available on all sources

### Slow Performance

Web scraping is slower than APIs (1-3 seconds per stock):
- **Normal**: 1-3 seconds per stock
- **With retries**: Up to 10 seconds

**Optimization:**
```env
CHECK_INTERVAL_MINUTES=30  # Reduce frequency
```

### Website Blocking

If a website blocks you:
1. **Increase delays** between requests
2. **Rotate sources** (already done automatically)
3. **Add delays** in `stock_fetcher.py` (already has 3-second delays)

## Best Practices

### For Production Use

1. **Enable web scraping** in `.env`:
   ```env
   USE_WEB_SCRAPING=true
   CHECK_INTERVAL_MINUTES=30
   ```

2. **Monitor logs** for failures:
   ```bash
   tail -f data/stocktracker.log
   ```

3. **Track 5-10 stocks max** to avoid being flagged

### For Development/Testing

1. **Use API first** (faster for testing)
2. **Switch to web scraping** if you hit rate limits
3. **Test one stock at a time** to verify sources

## Comparison: API vs Web Scraping

| Feature | Yahoo Finance API | Web Scraping |
|---------|-------------------|--------------|
| Speed | Fast (< 1s) | Slower (1-3s) |
| Rate Limits | Yes (strict) | No |
| Reliability | Low (429 errors) | High |
| Maintenance | Low | Medium (selectors may change) |
| Data Sources | 1 | 3+ |
| Best For | Quick tests | Production use |

## Recommended Configuration

For most users, we recommend:

```env
# .env
USE_WEB_SCRAPING=true
CHECK_INTERVAL_MINUTES=30
```

```json
// config/stocks.json
{
  "stocks": [
    {"symbol": "AAPL", "upper_threshold": 300.0, "lower_threshold": 200.0},
    {"symbol": "GOOGL", "upper_threshold": 200.0, "lower_threshold": 150.0},
    {"symbol": "MSFT", "upper_threshold": 500.0, "lower_threshold": 400.0}
  ]
}
```

This configuration:
- ✅ No rate limiting issues
- ✅ Checks every 30 minutes
- ✅ Tracks 3 stocks reliably
- ✅ Falls back to API if scraping fails

## Legal & Ethical Considerations

### Is web scraping legal?

For **personal, non-commercial use** (like StockTracker):
- ✅ Generally legal for publicly accessible data
- ✅ Financial data on public websites is meant to be viewed
- ✅ You're not redistributing or selling the data
- ✅ You're using reasonable request rates

### Best Practices:
- ✅ Use reasonable intervals (30+ minutes)
- ✅ Respect robots.txt (public financial data is typically allowed)
- ✅ Don't overload servers with requests
- ✅ Include user-agent headers (already implemented)
- ✅ Use for personal portfolio tracking only

### What NOT to do:
- ❌ Make hundreds of requests per minute
- ❌ Resell or redistribute the data
- ❌ Use for commercial purposes without permission
- ❌ Circumvent paywalls or authentication

## Adding New Data Sources

Want to add more sources? Edit `src/web_scraper.py`:

```python
def get_price_from_newsource(self, symbol: str) -> Optional[float]:
    """Fetch from your new source"""
    try:
        url = f"https://newsource.com/stock/{symbol}"
        response = self.session.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'lxml')

        # Find the price element
        price_elem = soup.select_one('span.price')
        if price_elem:
            price = self._extract_price(price_elem.get_text())
            if price:
                logger.info(f"Fetched {symbol}: ${price}")
                return price
        return None
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return None
```

Then add it to the sources list in `get_stock_price()`.

## Support

If you encounter issues with web scraping:
1. Check `data/stocktracker.log` for errors
2. Test individual sources manually
3. Verify the stock symbol is correct
4. Try a different data source
5. Fall back to API mode if needed

## Future Enhancements

Potential improvements:
- [ ] Add more data sources (Investing.com, Bloomberg, etc.)
- [ ] Implement caching to reduce requests
- [ ] Add proxy support for high-volume usage
- [ ] Support for cryptocurrency prices
- [ ] Historical data scraping
- [ ] Automatic selector updates
