# StockTracker Project Context

## Project Overview
StockTracker is a Python-based application that monitors stock prices and sends email alerts when prices cross user-defined thresholds. It's designed to be simple, containerized, and easy to deploy.

## Technology Stack
- **Language**: Python 3.11+
- **Stock Data**: Yahoo Finance API (via yfinance library)
- **Scheduling**: APScheduler for periodic checks
- **Notifications**: SMTP email
- **Deployment**: Docker & Docker Compose
- **Configuration**: JSON files + environment variables

## Project Structure
```
StockTracker/
├── src/                        # Application source code
│   ├── stock_fetcher.py       # Fetches real-time stock prices
│   ├── threshold_checker.py   # Compares prices against thresholds
│   ├── email_notifier.py      # Sends email alerts
│   └── main.py                # Main application with scheduler
├── config/                     # Configuration files
│   └── stocks.json            # Stock symbols and thresholds
├── data/                       # Runtime data (logs, potential DB)
│   └── stocktracker.log       # Application logs
├── .env                        # Environment variables (not in git)
├── .env.example               # Environment template
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container definition
└── docker-compose.yml         # Docker orchestration
```

## Core Components

### 1. StockFetcher (src/stock_fetcher.py)
- Fetches current stock prices from Yahoo Finance
- Uses yfinance library (no API key required)
- Methods:
  - `get_stock_price(symbol)`: Fetches single stock price
  - `get_multiple_prices(symbols)`: Batch fetch for multiple stocks

### 2. ThresholdChecker (src/threshold_checker.py)
- Loads stock configuration from `config/stocks.json`
- Compares current prices against upper/lower thresholds
- Returns list of threshold violations
- Methods:
  - `load_stocks()`: Loads JSON configuration
  - `check_thresholds(prices)`: Checks for violations
  - `get_tracked_symbols()`: Returns list of symbols to track

### 3. EmailNotifier (src/email_notifier.py)
- Sends email alerts via SMTP
- Configurable via environment variables
- Supports common email providers (Gmail, Outlook, Yahoo)
- Methods:
  - `send_alert(violations)`: Sends formatted email alert

### 4. Main Application (src/main.py)
- Orchestrates all components
- Uses APScheduler for periodic checks
- Configurable check interval (default: 15 minutes)
- Logs to console and file

## Configuration

### Stock Configuration (config/stocks.json)
```json
{
  "stocks": [
    {
      "symbol": "AAPL",
      "upper_threshold": 200.0,    // Optional
      "lower_threshold": 150.0     // Optional
    }
  ]
}
```

### Environment Variables (.env)
- `SMTP_SERVER`: Email server (e.g., smtp.gmail.com)
- `SMTP_PORT`: SMTP port (typically 587)
- `SENDER_EMAIL`: Email to send from
- `SENDER_PASSWORD`: Email password/app password
- `RECIPIENT_EMAIL`: Email to receive alerts
- `CHECK_INTERVAL_MINUTES`: How often to check (default: 15)

## Key Design Decisions

1. **Yahoo Finance API**: Chosen for simplicity (no API key required)
2. **JSON Configuration**: Easy to edit, no database needed for simple use
3. **SMTP Email**: Universal, works with any email provider
4. **Docker Ready**: Easy deployment anywhere Docker runs
5. **Modular Design**: Each component is independent and testable

## Development Workflow

### Local Testing (Without Docker)
```bash
python -m venv venv
pip install -r requirements.txt
cp .env.example .env
# Edit .env with credentials
python src/main.py
```

### Docker Deployment
```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## Common Tasks

### Adding a New Stock
1. Edit `config/stocks.json`
2. Add new entry with symbol and thresholds
3. Restart application (or wait for next check cycle)

### Changing Check Interval
1. Edit `.env` file
2. Update `CHECK_INTERVAL_MINUTES`
3. Restart application

### Troubleshooting
- Check `data/stocktracker.log` for errors
- Verify stock symbols on Yahoo Finance website
- For Gmail: Must use App Password, not regular password
- Email failures don't stop price checking

## Future Enhancement Ideas
- Database support for historical tracking
- Web dashboard for monitoring
- SMS/Slack/Discord notifications
- Multiple recipients per stock
- Technical indicators (RSI, MACD)
- Alert cooldown to prevent spam
- Price change percentage alerts
- Market hours awareness

## Important Notes
- Run from project root: `python src/main.py` (not from inside src/)
- Yahoo Finance may have rate limits - increase interval if needed
- Gmail requires 2FA + App Password
- Application continues running even if email fails
- Logs are essential for debugging
