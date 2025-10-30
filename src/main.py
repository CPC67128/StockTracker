"""
StockTracker Main Application
Monitors stock prices and sends alerts when thresholds are crossed
"""
import logging
import os
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from stock_fetcher import StockFetcher
from threshold_checker import ThresholdChecker
from email_notifier import EmailNotifier
from colorama import Fore, Style, init
from datetime import datetime

# Initialize colorama for Windows compatibility
init(autoreset=True)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/stocktracker.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class StockTracker:
    """Main application class for stock tracking and alerting"""

    def __init__(self):
        self.fetcher = StockFetcher()
        self.checker = ThresholdChecker(config_path='config/stocks.json')
        self.notifier = EmailNotifier()
        self.scheduler = BlockingScheduler()
        self.last_prices = {}  # Cache last fetched prices
        self.last_daily_email_date = None  # Track when daily email was last sent
        self.startup_email_sent = False  # Track if startup email was sent

    def check_stocks(self):
        """Main checking routine - fetches prices and checks thresholds"""
        logger.info("Starting stock check cycle...")

        # Check for configuration changes and reload if needed
        if self.checker.reload_if_changed():
            logger.info("Stock configuration has been reloaded with updated values")

        # Get tracked symbols
        symbols = self.checker.get_tracked_symbols()
        if not symbols:
            logger.warning("No stocks configured for tracking")
            return

        # Get display names for logging
        display_names = self.checker.get_stock_display_names()
        logger.info(f"Tracking {len(symbols)} stocks: {', '.join(display_names)}")

        # Get symbol to name mapping for fetcher logging
        symbol_to_name = self.checker.get_symbol_to_name_map()

        # Fetch current prices
        prices = self.fetcher.get_multiple_prices(symbols, symbol_to_name)

        # Cache the prices for potential reuse
        self.last_prices = prices

        # Display colored price summary
        self._display_price_summary(prices, symbol_to_name)

        # Check for threshold violations
        violations = self.checker.check_thresholds(prices)

        # Send alerts if violations found
        if violations:
            logger.warning(f"Found {len(violations)} threshold violation(s)")
            self.notifier.send_alert(violations)
        else:
            logger.info("No threshold violations detected")

        # Check if we should send daily email (once per day, between 9 AM - 5 PM)
        self._check_and_send_daily_email()

        logger.info("Stock check cycle completed")

    def _check_and_send_daily_email(self):
        """Check if we should send daily email (startup or once per day between 9 AM - 5 PM)"""
        now = datetime.now()
        current_hour = now.hour
        current_date = now.date()

        # Always send on first startup
        if not self.startup_email_sent:
            logger.info(f"Sending daily email on startup")
            self.send_daily_summary()
            self.startup_email_sent = True
            self.last_daily_email_date = current_date
            return

        # Check if we're in the 9 AM - 5 PM window
        if current_hour < 9 or current_hour >= 17:
            logger.debug(f"Outside email window (9 AM - 5 PM), current time: {now.strftime('%H:%M')}")
            return

        # Check if we already sent email today
        if self.last_daily_email_date == current_date:
            logger.debug(f"Daily email already sent today ({current_date})")
            return

        # Send the daily email
        logger.info(f"Sending daily email (first run between 9 AM - 5 PM today)")
        self.send_daily_summary()
        self.last_daily_email_date = current_date

    def send_daily_summary(self):
        """Send daily summary email with all stock prices and thresholds"""
        logger.info("Preparing daily summary email...")

        # Use cached prices from last check_stocks() call
        prices = self.last_prices

        if not prices:
            logger.warning("No cached prices available, skipping daily summary")
            return

        # Build stocks data for email
        stocks_data = []
        for stock_config in self.checker.stocks:
            symbol = stock_config.get('symbol')
            stock_info = {
                'symbol': symbol,
                'name': stock_config.get('name', ''),
                'price': prices.get(symbol),
                'currency': stock_config.get('currency', 'EUR'),
                'initial_value': stock_config.get('initial_value'),
                'initial_date': stock_config.get('initial_date'),
                'upper_threshold': stock_config.get('upper_threshold'),
                'lower_threshold': stock_config.get('lower_threshold')
            }
            stocks_data.append(stock_info)

        # Send summary email
        self.notifier.send_daily_summary(stocks_data)
        logger.info("Daily summary email sent")

    def _display_price_summary(self, prices, symbol_to_name):
        """Display colored summary of stock prices vs thresholds"""
        print(f"\n{Style.BRIGHT}=== Stock Price Summary ==={Style.RESET_ALL}")
        logger.info("=== Stock Price Summary ===")

        for stock_config in self.checker.stocks:
            symbol = stock_config.get('symbol')
            name = stock_config.get('name', '')
            currency = stock_config.get('currency', 'EUR')
            upper_threshold = stock_config.get('upper_threshold')
            lower_threshold = stock_config.get('lower_threshold')
            initial_value = stock_config.get('initial_value')
            initial_date = stock_config.get('initial_date')

            if symbol not in prices or prices[symbol] is None:
                continue

            price = prices[symbol]
            display_name = f"{name} ({symbol})" if name else symbol

            # Calculate percentage to upper threshold
            # Formula: (current - initial) / (upper - initial) * 100
            percentage_text = ""
            percentage = None
            if initial_value and upper_threshold and upper_threshold > 0:
                if upper_threshold > initial_value:  # Only calculate if upper threshold is above initial value
                    percentage = ((price - initial_value) / (upper_threshold - initial_value)) * 100
                    percentage_text = f" / {percentage:.1f}% to target"

            # Calculate holding period (retention duration)
            holding_text = ""
            if initial_date:
                try:
                    purchase_date = datetime.strptime(initial_date, "%Y-%m-%d")
                    today = datetime.now()
                    days_held = (today - purchase_date).days

                    # Format as years and days or just days
                    if days_held >= 365:
                        years = days_held // 365
                        remaining_days = days_held % 365
                        holding_text = f" / Held: {years}y {remaining_days}d"
                    else:
                        holding_text = f" / Held: {days_held}d"
                except ValueError:
                    # Invalid date format, skip
                    pass

            # Determine color based on threshold status and percentage
            # Check if upper threshold is crossed (good news!)
            upper_threshold_crossed = upper_threshold and upper_threshold > 0 and price >= upper_threshold
            # Check if lower threshold is crossed (bad news)
            lower_threshold_crossed = lower_threshold and lower_threshold > 0 and price <= lower_threshold

            # Print with color to console
            if upper_threshold_crossed:
                # Green for upper threshold reached (target achieved!)
                print(f"{Fore.GREEN}{display_name}: {price:.4f} {currency} [TARGET REACHED]{percentage_text}{holding_text}{Style.RESET_ALL}")
                logger.info(f"{display_name}: {price:.4f} {currency} [TARGET REACHED]{percentage_text}{holding_text}")
            elif lower_threshold_crossed:
                # Red for lower threshold crossed (alert)
                print(f"{Fore.RED}{display_name}: {price:.4f} {currency} [ALERT] (lower threshold crossed!){percentage_text}{holding_text}{Style.RESET_ALL}")
                logger.warning(f"{display_name}: {price:.4f} {currency} [ALERT] (lower threshold crossed!){percentage_text}{holding_text}")
            elif percentage is not None and percentage < 0:
                # Red for negative percentage (below initial value)
                print(f"{Fore.RED}{display_name}: {price:.4f} {currency} [OK]{percentage_text}{holding_text}{Style.RESET_ALL}")
                logger.info(f"{display_name}: {price:.4f} {currency} [OK]{percentage_text}{holding_text}")
            else:
                # Blue for positive percentage (approaching target)
                print(f"{Fore.BLUE}{display_name}: {price:.4f} {currency} [OK]{percentage_text}{holding_text}{Style.RESET_ALL}")
                logger.info(f"{display_name}: {price:.4f} {currency} [OK]{percentage_text}{holding_text}")

        print()

    def run(self):
        """Start the stock tracker with scheduled checks"""
        # Get check interval from environment (default: every 15 minutes)
        check_interval = int(os.getenv('CHECK_INTERVAL_MINUTES', '15'))

        logger.info(f"StockTracker starting with {check_interval} minute check interval")

        # Run initial check immediately (will also send daily email if in time window)
        self.check_stocks()

        # Schedule periodic checks (daily email is checked within check_stocks)
        self.scheduler.add_job(
            self.check_stocks,
            'interval',
            minutes=check_interval,
            id='stock_check'
        )

        logger.info("Scheduler started. Press Ctrl+C to exit.")
        logger.info("Daily email will be sent on first check between 9 AM - 5 PM each day")
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("StockTracker shutting down...")


if __name__ == '__main__':
    tracker = StockTracker()
    tracker.run()
