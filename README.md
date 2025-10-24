# StockTracker

A Python-based stock monitoring application that tracks stock prices and sends email alerts when they cross defined thresholds. Fully containerized with Docker for easy deployment.

## Features

- Real-time stock price monitoring using Yahoo Finance **or web scraping**
- **Multiple data sources** (Google Finance, MarketWatch, Boursorama)
- **No API rate limits** with web scraping mode
- Configurable upper and lower price thresholds per stock
- Email notifications when thresholds are crossed
- Scheduled periodic checks (configurable interval)
- Docker containerized for portable deployment
- Simple JSON-based configuration
- Automatic fallback between data sources

## Project Structure

```
StockTracker/
├── src/
│   ├── stock_fetcher.py       # Fetches stock prices (API or web scraping)
│   ├── web_scraper.py         # Web scraping implementation
│   ├── threshold_checker.py   # Checks prices against thresholds
│   ├── email_notifier.py      # Sends email alerts
│   └── main.py                # Main application entry point
├── config/
│   └── stocks.json            # Stock symbols and thresholds
├── data/
│   └── stocktracker.log       # Application logs
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Docker compose configuration
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── README.md                  # This file
├── TROUBLESHOOTING.md         # Troubleshooting guide
└── WEB_SCRAPING.md           # Web scraping guide
```

## Prerequisites

- Docker and Docker Compose (for containerized deployment)
- OR Python 3.11+ (for local development)

## Quick Start with Docker

### 1. Clone and Configure

```bash
cd StockTracker
```

### 2. Set up Environment Variables

Copy the example environment file and edit it with your details:

```bash
cp .env.example .env
```

Edit `.env` with your email configuration:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient@example.com
CHECK_INTERVAL_MINUTES=15
```

**Note for Gmail users:** You need to use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

### 3. Configure Stocks to Track

Edit `config/stocks.json` to add your stocks and thresholds:

```json
{
  "stocks": [
    {
      "symbol": "AAPL",
      "upper_threshold": 200.0,
      "lower_threshold": 150.0
    },
    {
      "symbol": "GOOGL",
      "upper_threshold": 180.0,
      "lower_threshold": 140.0
    }
  ]
}
```

### 4. Run with Docker Compose

```bash
docker-compose up -d
```

View logs:
```bash
docker-compose logs -f
```

Stop the application:
```bash
docker-compose down
```

## Local Development (Without Docker)

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file as described above.

### 3. Run Application

```bash
python src/main.py
```

**Note:** Run from the project root directory, not from inside the `src/` folder.

## Configuration

### Stock Configuration (`config/stocks.json`)

- `symbol`: Stock ticker symbol (e.g., "AAPL", "GOOGL")
- `upper_threshold`: Alert when price goes above this value (optional)
- `lower_threshold`: Alert when price goes below this value (optional)

You can omit either threshold if you only want to track one direction.

### Environment Variables (`.env`)

- `SMTP_SERVER`: Your email provider's SMTP server
- `SMTP_PORT`: SMTP port (typically 587 for TLS)
- `SENDER_EMAIL`: Email address to send from
- `SENDER_PASSWORD`: Email password or app password
- `RECIPIENT_EMAIL`: Email address to receive alerts
- `CHECK_INTERVAL_MINUTES`: How often to check prices (default: 15)
- `USE_WEB_SCRAPING`: Set to `true` to use web scraping instead of Yahoo Finance API (default: false)

### Data Source: API vs Web Scraping

**Recommended: Use Web Scraping** to avoid Yahoo Finance rate limits.

Edit your `.env` file:
```env
USE_WEB_SCRAPING=true
```

**Benefits:**
- ✅ No rate limiting (429 errors)
- ✅ Multiple data sources (Google Finance, MarketWatch, Boursorama)
- ✅ Automatic fallback if one source fails
- ✅ More reliable for production use

See [WEB_SCRAPING.md](WEB_SCRAPING.md) for detailed information.

### Common Email Providers

**Gmail:**
- Server: `smtp.gmail.com`
- Port: `587`
- Requires [App Password](https://support.google.com/accounts/answer/185833)

**Outlook/Hotmail:**
- Server: `smtp-mail.outlook.com`
- Port: `587`

**Yahoo:**
- Server: `smtp.mail.yahoo.com`
- Port: `587`

**Other Providers:**
- For other email providers, search for their SMTP settings
- Most use port 587 for TLS or 465 for SSL
- Some providers (like ProtonMail) may require Bridge software

## How It Works

1. The application loads stock configurations from `config/stocks.json`
2. Every X minutes (configured in `.env`), it:
   - Fetches current prices from Yahoo Finance
   - Compares prices against configured thresholds
   - Sends email alerts for any violations
3. Logs all activity to `data/stocktracker.log`

## Testing Without Email

To test the application without configuring email (useful for initial testing):

1. Leave the email credentials in `.env` as placeholder values
2. Run the application: `python src/main.py`
3. The app will fetch stock prices and check thresholds
4. Email sending will fail but the app continues logging all activity
5. Check console output and `data/stocktracker.log` to verify it's working

## Example Output

When running successfully, you'll see output like:

```
2025-10-24 10:00:00 - __main__ - INFO - StockTracker starting with 15 minute check interval
2025-10-24 10:00:00 - __main__ - INFO - Starting stock check cycle...
2025-10-24 10:00:00 - __main__ - INFO - Tracking 3 stocks: AAPL, GOOGL, MSFT
2025-10-24 10:00:01 - stock_fetcher - INFO - Fetched AAPL: $175.50
2025-10-24 10:00:02 - stock_fetcher - INFO - Fetched GOOGL: $142.30
2025-10-24 10:00:03 - stock_fetcher - INFO - Fetched MSFT: $420.15
2025-10-24 10:00:03 - __main__ - INFO - No threshold violations detected
2025-10-24 10:00:03 - __main__ - INFO - Stock check cycle completed
```

## Troubleshooting

**No email received:**
- Check your email credentials in `.env`
- For Gmail, ensure you're using an App Password (not regular password)
- Verify 2-Step Verification is enabled in your Google Account
- Check `data/stocktracker.log` for error messages
- Test with a different email provider if Gmail isn't working

**Stock prices not updating:**
- Verify stock symbols are correct (use Yahoo Finance ticker symbols)
- Check internet connectivity
- Review logs for API errors
- Yahoo Finance may have rate limits - try increasing CHECK_INTERVAL_MINUTES

**"No data returned for symbol" error:**
- Double-check the stock ticker symbol is correct
- Some stocks may not be available on Yahoo Finance
- Try searching for the stock on [Yahoo Finance](https://finance.yahoo.com/) first

**Container not starting:**
- Ensure `.env` file exists and is properly configured
- Check Docker logs: `docker-compose logs`
- Verify config/stocks.json is valid JSON

**Windows-specific issues:**
- If activation fails, run directly: `python src/main.py`
- Ensure Python is added to your PATH
- Use forward slashes or escaped backslashes in file paths

## Advanced Usage

### Running as a Background Service

**Linux/Mac (using systemd):**

Create a systemd service file at `/etc/systemd/system/stocktracker.service`:

```ini
[Unit]
Description=StockTracker Service
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/StockTracker
ExecStart=/path/to/StockTracker/venv/bin/python src/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then enable and start:
```bash
sudo systemctl enable stocktracker
sudo systemctl start stocktracker
```

**Windows (using Task Scheduler):**

1. Open Task Scheduler
2. Create a new task
3. Set trigger to "At startup" or specific time
4. Set action to run: `python.exe` with arguments: `c:\path\to\StockTracker\src\main.py`
5. Set "Start in" to: `c:\path\to\StockTracker`

### Customizing Check Intervals

You can run different check intervals for different stocks by running multiple instances:

1. Create separate config files: `stocks-frequent.json`, `stocks-daily.json`
2. Create separate .env files with different intervals
3. Run multiple instances pointing to different configs

### Adding More Stocks

Simply edit [config/stocks.json](config/stocks.json) and add new entries. The application will automatically pick them up on the next check cycle (or restart the app).

### Monitoring Multiple Thresholds

You can set both upper and lower thresholds, or just one:

```json
{
  "symbol": "TSLA",
  "upper_threshold": 300.0,
  "lower_threshold": 200.0
}
```

Or only upper:
```json
{
  "symbol": "NVDA",
  "upper_threshold": 500.0
}
```

## Dependencies

- **yfinance**: Fetches stock data from Yahoo Finance
- **requests**: HTTP library for API calls
- **APScheduler**: Job scheduling for periodic checks
- **python-dotenv**: Environment variable management

## Contributing

Contributions are welcome! Some ideas for enhancements:

- Add database support (SQLite/PostgreSQL) for historical tracking
- Web dashboard for monitoring stocks
- SMS notifications via Twilio
- Slack/Discord webhook support
- Technical indicators (RSI, MACD, etc.)
- Multiple alert recipients
- Alert cooldown to prevent spam

## License

This project is open source and available under the MIT License.
