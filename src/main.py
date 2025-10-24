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

        logger.info(f"Tracking {len(symbols)} stocks: {', '.join(symbols)}")

        # Fetch current prices
        prices = self.fetcher.get_multiple_prices(symbols)

        # Check for threshold violations
        violations = self.checker.check_thresholds(prices)

        # Send alerts if violations found
        if violations:
            logger.warning(f"Found {len(violations)} threshold violation(s)")
            self.notifier.send_alert(violations)
        else:
            logger.info("No threshold violations detected")

        logger.info("Stock check cycle completed")

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
