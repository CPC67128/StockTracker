# StockTracker Project Context

## Project Overview
StockTracker is a Python-based application that monitors stock prices and sends email alerts when prices cross user-defined thresholds. It's designed to be simple, containerized, and easy to deploy.

## Technology Stack
- **Language**: Python 3.11+
- **Stock Data**: Yahoo Finance API (via yfinance library) + Web scraping (BeautifulSoup, lxml)
- **Scheduling**: APScheduler for periodic checks
- **Notifications**: SMTP email with HTML formatting
- **Deployment**: Docker & Docker Compose, systemd service
- **Configuration**: JSON files + environment variables
- **File Monitoring**: File modification time tracking for hot-reload
- **UI**: Colorama for colored console output

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
- **Hot-reload**: Automatically detects and reloads config file changes
- Compares current prices against upper/lower thresholds
- Returns list of threshold violations
- Methods:
  - `load_stocks()`: Loads JSON configuration and tracks modification time
  - `check_for_config_changes()`: Checks if config file has been modified
  - `reload_if_changed()`: Reloads configuration if file changed
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
- **Hot-reload integration**: Checks for config changes before each stock check
- Daily summary email (sent on startup and once per day between 9 AM - 5 PM)
- Color-coded console output (Green: target reached, Blue: progress, Red: alert/loss)
- Logs to console and file

## Configuration

### Stock Configuration (config/stocks.json)
```json
{
  "stocks": [
    {
      "symbol": "AAPL",              // Stock ticker or ISIN code
      "name": "Apple Inc.",          // Display name
      "sector": "Tech",              // Optional sector/category
      "currency": "USD",             // Currency (EUR, USD, GBP, etc.)
      "initial_value": 150.0,        // Purchase price
      "initial_quantity": 10,        // Number of shares
      "initial_date": "2024-01-15",  // Purchase date
      "upper_threshold": 200.0,      // Target price (optional)
      "lower_threshold": 140.0       // Alert price (optional)
    }
  ]
}
```

**Hot-reload**: Changes to this file are automatically detected and applied on the next check cycle. No restart required!

### Environment Variables (.env)
- `SMTP_SERVER`: Email server (e.g., smtp.gmail.com)
- `SMTP_PORT`: SMTP port (typically 587)
- `SENDER_EMAIL`: Email to send from
- `SENDER_PASSWORD`: Email password/app password
- `RECIPIENT_EMAIL`: Email to receive alerts
- `CHECK_INTERVAL_MINUTES`: How often to check (default: 15)

## Key Design Decisions

1. **Dual Data Sources**: Yahoo Finance API + web scraping for reliability and French stock support
2. **JSON Configuration**: Easy to edit, no database needed for simple use
3. **Hot-Reload**: File modification time tracking allows config changes without restart
4. **SMTP Email**: Universal, works with any email provider
5. **Docker + systemd**: Flexible deployment options (containerized or native Linux service)
6. **Modular Design**: Each component is independent and testable
7. **Multi-Currency**: Supports EUR, USD, GBP, JPY, CHF with code display
8. **Color-Coded Output**: Visual feedback for stock performance (green/blue/red)

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
2. Add new entry with symbol, name, currency, thresholds, etc.
3. Save the file - **hot-reload automatically applies changes on next check cycle**
4. Monitor logs to confirm reload: `tail -f data/stocktracker.log`

### Changing Check Interval
1. Edit `.env` file
2. Update `CHECK_INTERVAL_MINUTES`
3. Restart application

### Troubleshooting
- Check `data/stocktracker.log` for errors
- Verify stock symbols on Yahoo Finance website
- For Gmail: Must use App Password, not regular password
- Email failures don't stop price checking

## Recent Features Implemented
- **Hot-reload configuration**: File modification time tracking detects changes to stocks.json automatically
- **Multi-currency support**: Track stocks in EUR, USD, GBP, JPY, CHF with proper display
- **Web scraping**: Multiple sources (Boursorama, MarketWatch, Google Finance) for French/ISIN stocks
- **Daily email summaries**: Sent on startup and once per day between 9 AM - 5 PM
- **Color-coded output**: Green (target reached), Blue (progress), Red (alert/loss)
- **Holding period calculation**: Shows days held and percentage to target
- **Systemd service**: Full Linux VPS deployment support

## Future Enhancement Ideas
- Database support for historical tracking
- Web dashboard for monitoring
- SMS/Slack/Discord notifications
- Multiple recipients per stock
- Technical indicators (RSI, MACD)
- Alert cooldown to prevent spam
- Market hours awareness
- Portfolio value tracking

## Important Notes
- Run from project root: `python src/main.py` (not from inside src/)
- Yahoo Finance may have rate limits - increase interval if needed
- Gmail requires 2FA + App Password
- Application continues running even if email fails
- Logs are essential for debugging
- **Hot-reload**: Edit stocks.json anytime - changes auto-detected on next check cycle
- French PEA stocks use ISIN codes (e.g., FR0000121014) with Boursorama web scraping
- Color coding: Green = target reached, Blue = making progress, Red = alert or loss
