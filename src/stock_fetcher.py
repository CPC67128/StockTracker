"""
Stock Fetcher Module
Fetches current stock prices using Yahoo Finance API or web scraping
"""
import yfinance as yf
from typing import Dict, Optional
import logging
import time
import os

logger = logging.getLogger(__name__)


class StockFetcher:
    """Fetches stock prices from Yahoo Finance API or web scraping"""

    def __init__(self, use_web_scraping: bool = None):
        """
        Initialize StockFetcher

        Args:
            use_web_scraping: If True, use web scraping. If False, use API.
                            If None, read from environment variable USE_WEB_SCRAPING
        """
        self.cache = {}

        # Determine which method to use
        if use_web_scraping is None:
            use_web_scraping = os.getenv('USE_WEB_SCRAPING', 'false').lower() == 'true'

        self.use_web_scraping = use_web_scraping

        # Initialize web scraper if needed
        self.web_scraper = None
        if self.use_web_scraping:
            try:
                from web_scraper import WebScraper
                self.web_scraper = WebScraper()
                logger.info("Using web scraping for stock prices")
            except ImportError:
                logger.warning("Web scraper not available, falling back to API")
                self.use_web_scraping = False

    def get_stock_price(self, symbol: str, retry_count: int = 3, name: str = '') -> Optional[float]:
        """
        Fetch the current price for a given stock symbol

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
            retry_count: Number of retry attempts (default: 3)
            name: Optional stock name for better logging

        Returns:
            Current stock price or None if fetch fails
        """
        # Create display name for logging
        display_name = f"{name} ({symbol})" if name else symbol

        # Use web scraping if enabled
        if self.use_web_scraping and self.web_scraper:
            logger.info(f"Fetching {display_name} via web scraping")
            price = self.web_scraper.get_stock_price(symbol, name=name)
            if price:
                return price
            logger.warning(f"Web scraping failed for {display_name}, trying API fallback")

        # Use Yahoo Finance API (original method)
        for attempt in range(retry_count):
            try:
                # Add user agent to reduce rate limiting
                ticker = yf.Ticker(symbol)
                ticker.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

                # Try multiple periods to get data
                for period in ['1d', '5d', '1mo']:
                    try:
                        data = ticker.history(period=period)

                        if not data.empty:
                            current_price = data['Close'].iloc[-1]
                            logger.info(f"Fetched {symbol}: ${current_price:.4f} (period: {period})")
                            return float(current_price)
                    except Exception as period_error:
                        logger.debug(f"Period {period} failed for {symbol}: {str(period_error)}")
                        continue

                # If history failed, try using info as fallback
                try:
                    info = ticker.info
                    if info and 'currentPrice' in info:
                        current_price = info['currentPrice']
                        logger.info(f"Fetched {symbol} from info: ${current_price:.4f}")
                        return float(current_price)
                    elif info and 'regularMarketPrice' in info:
                        current_price = info['regularMarketPrice']
                        logger.info(f"Fetched {symbol} from regularMarketPrice: ${current_price:.4f}")
                        return float(current_price)
                except Exception as info_error:
                    logger.debug(f"Info fallback failed for {symbol}: {str(info_error)}")

                logger.warning(f"No data returned for symbol: {symbol} (attempt {attempt + 1}/{retry_count})")

                # Wait before retrying
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s

            except Exception as e:
                logger.error(f"Error fetching price for {symbol} (attempt {attempt + 1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)

        logger.error(f"Failed to fetch {symbol} after {retry_count} attempts")
        return None

    def get_multiple_prices(self, symbols: list, symbol_to_name: Dict[str, str] = None) -> Dict[str, Optional[float]]:
        """
        Fetch prices for multiple stock symbols

        Args:
            symbols: List of stock ticker symbols
            symbol_to_name: Optional mapping of symbols to names for better logging

        Returns:
            Dictionary mapping symbols to their current prices
        """
        if symbol_to_name is None:
            symbol_to_name = {}

        prices = {}
        for i, symbol in enumerate(symbols):
            name = symbol_to_name.get(symbol, '')
            prices[symbol] = self.get_stock_price(symbol, name=name)
            # Add delay between requests to avoid rate limiting
            if i < len(symbols) - 1:  # Don't delay after last symbol
                time.sleep(3)  # Wait 3 seconds between each request
        return prices
