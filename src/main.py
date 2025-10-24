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

    def check_stocks(self):
        """Main checking routine - fetches prices and checks thresholds"""
        logger.info("Starting stock check cycle...")

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

        logger.info("Stock check cycle completed")

    def _display_price_summary(self, prices, symbol_to_name):
        """Display colored summary of stock prices vs thresholds"""
        print(f"\n{Style.BRIGHT}=== Stock Price Summary ==={Style.RESET_ALL}")

        for stock_config in self.checker.stocks:
            symbol = stock_config.get('symbol')
            name = stock_config.get('name', '')
            upper_threshold = stock_config.get('upper_threshold')
            lower_threshold = stock_config.get('lower_threshold')

            if symbol not in prices or prices[symbol] is None:
                continue

            price = prices[symbol]
            display_name = f"{name} ({symbol})" if name else symbol

            # Determine color based on threshold status
            # Blue if within thresholds, Red if violated
            is_within_thresholds = True

            # Check if price violates thresholds
            if upper_threshold and upper_threshold > 0 and price >= upper_threshold:
                is_within_thresholds = False
            if lower_threshold and lower_threshold > 0 and price <= lower_threshold:
                is_within_thresholds = False

            # Print with color
            if is_within_thresholds:
                print(f"{Fore.BLUE}{display_name}: {price:.4f}€ [OK] (within thresholds){Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{display_name}: {price:.4f}€ [ALERT] (threshold crossed!){Style.RESET_ALL}")

        print()

    def run(self):
        """Start the stock tracker with scheduled checks"""
        # Get check interval from environment (default: every 15 minutes)
        check_interval = int(os.getenv('CHECK_INTERVAL_MINUTES', '15'))

        logger.info(f"StockTracker starting with {check_interval} minute check interval")

        # Run initial check immediately
        self.check_stocks()

        # Schedule periodic checks
        self.scheduler.add_job(
            self.check_stocks,
            'interval',
            minutes=check_interval,
            id='stock_check'
        )

        logger.info("Scheduler started. Press Ctrl+C to exit.")
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("StockTracker shutting down...")


if __name__ == '__main__':
    tracker = StockTracker()
    tracker.run()
