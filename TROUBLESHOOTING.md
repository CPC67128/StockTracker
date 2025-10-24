# StockTracker Troubleshooting Guide

## Yahoo Finance Rate Limiting (429 Errors)

### Symptoms
```
ERROR:yfinance:429 Client Error: Too Many Requests
ERROR:yfinance:Failed to get ticker 'AAPL' reason: Expecting value: line 1 column 1 (char 0)
```

### Causes
- Yahoo Finance API has strict rate limits on the free tier
- Making too many requests in a short time
- IP address temporarily blocked

### Solutions

#### 1. Wait and Retry (Recommended for testing)
- **Wait Time**: 10-15 minutes
- Rate limits typically reset after this period
- Then try running the application again

#### 2. Increase Check Interval
Edit your `.env` file:
```env
CHECK_INTERVAL_MINUTES=30  # or higher (60, 120, etc.)
```

The longer the interval, the less likely you'll hit rate limits.

#### 3. Reduce Number of Tracked Stocks
If tracking many stocks:
- Start with 1-3 stocks for testing
- The app adds 3-second delays between requests
- Fewer stocks = fewer API calls = less rate limiting

#### 4. Use a VPN (Advanced)
- Yahoo may rate-limit by IP address
- Switching IP addresses via VPN may help
- Not recommended for long-term solution

#### 5. Consider Alternative Stock APIs
If rate limiting persists, consider these alternatives:

**Alpha Vantage (Free Tier)**
- 25 requests per day
- Requires API key (free)
- More reliable than Yahoo Finance
- https://www.alphavantage.co/

**Financial Modeling Prep (Free Tier)**
- 250 requests per day
- Requires API key (free)
- Good documentation
- https://financialmodelingprep.com/

**IEX Cloud (Free Tier)**
- 50,000 messages/month free
- Requires API key
- Professional quality
- https://iexcloud.io/

### Testing Without Rate Limits

#### Test with Mock Data
Create a test version that doesn't call the API:

```python
# test_local.py
from src.threshold_checker import ThresholdChecker
from src.email_notifier import EmailNotifier

# Simulate prices
test_prices = {
    'AAPL': 175.50,
    'GOOGL': 142.30,
    'MSFT': 420.15
}

checker = ThresholdChecker()
violations = checker.check_thresholds(test_prices)
print(f"Violations found: {violations}")

if violations:
    notifier = EmailNotifier()
    notifier.send_alert(violations)
```

Run with: `python test_local.py`

#### Use Longer Delays Between Stocks
The app already adds 3-second delays. If still rate-limited, increase it:

Edit `src/stock_fetcher.py` line 90:
```python
time.sleep(5)  # Change from 3 to 5 or more seconds
```

## Best Practices to Avoid Rate Limiting

1. **Start Small**: Test with 1-2 stocks first
2. **Longer Intervals**: Use 30+ minute check intervals
3. **Off-Peak Hours**: Run during non-market hours when API is less busy
4. **Docker Deployment**: Once tested, deploy with Docker for stable operation
5. **Monitor Logs**: Check `data/stocktracker.log` for issues

## Current Implementation

The StockTracker already includes these protections:
- ✅ 3-second delays between stock requests
- ✅ Retry logic with exponential backoff (1s, 2s, 4s)
- ✅ Multiple data source fallbacks (history, info, regularMarketPrice)
- ✅ User-Agent header to appear as a browser
- ✅ Graceful error handling (continues even if some stocks fail)

## Recommended Configuration for Reliability

For production use without hitting rate limits:

```env
# .env file
CHECK_INTERVAL_MINUTES=60  # Check once per hour
```

```json
// config/stocks.json - Start with 3-5 stocks
{
  "stocks": [
    {"symbol": "AAPL", "upper_threshold": 200.0, "lower_threshold": 150.0},
    {"symbol": "GOOGL", "upper_threshold": 180.0, "lower_threshold": 140.0},
    {"symbol": "MSFT", "upper_threshold": 450.0, "lower_threshold": 400.0"}
  ]
}
```

This configuration will:
- Check 3 stocks once per hour
- Total: 72 API calls per day (well under typical limits)
- Minimal risk of rate limiting

## If You've Been Rate Limited

**Immediate Actions:**
1. Stop the application if running
2. Wait 15-30 minutes
3. Reduce tracked stocks to 2-3
4. Increase `CHECK_INTERVAL_MINUTES` to 60 or higher
5. Restart the application

**Long-term:**
- Consider switching to a paid API service if you need more frequent updates
- Use a VPS/cloud service (different IP than your development machine)
- Implement caching to reduce redundant API calls
