"""
Web Scraper Module
Fetches stock prices by scraping public financial websites
Alternative to API-based fetching to avoid rate limits
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional
import logging
import re

logger = logging.getLogger(__name__)


class WebScraper:
    """Scrapes stock prices from various financial websites"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })

    def get_price_from_boursorama(self, symbol: str) -> Optional[float]:
        """
        Fetch stock price from Boursorama (French financial site)

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')

        Returns:
            Current stock price or None if fetch fails
        """
        try:
            # Boursorama uses format like: /cours/1rPAPPL/ for Apple
            # We need to convert symbol to Boursorama format
            # For US stocks, typically: 1rP{SYMBOL}
            boursorama_symbol = f"1rP{symbol}"
            url = f"https://www.boursorama.com/cours/{boursorama_symbol}/"

            logger.info(f"Fetching {symbol} from Boursorama: {url}")
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                logger.warning(f"Boursorama returned status {response.status_code} for {symbol}")
                return None

            soup = BeautifulSoup(response.text, 'lxml')

            # Look for the price in common CSS selectors
            # Boursorama typically has price in a span with specific classes
            price_selectors = [
                'span.c-instrument--last',
                'span.c-faceplate__price',
                'div.c-faceplate__price span',
                '[data-ist-last]',
            ]

            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    # Extract number from text (handle formats like "175,50 USD" or "175.50")
                    price = self._extract_price(price_text)
                    if price:
                        logger.info(f"Fetched {symbol} from Boursorama: ${price:.2f}")
                        return price

            logger.warning(f"Could not find price element for {symbol} on Boursorama")
            return None

        except Exception as e:
            logger.error(f"Error fetching {symbol} from Boursorama: {str(e)}")
            return None

    def get_price_from_google_finance(self, symbol: str) -> Optional[float]:
        """
        Fetch stock price from Google Finance

        Args:
            symbol: Stock ticker symbol with exchange (e.g., 'NASDAQ:AAPL')

        Returns:
            Current stock price or None if fetch fails
        """
        try:
            # Google Finance format: /quote/AAPL:NASDAQ
            if ':' not in symbol:
                # Default to NASDAQ for US stocks
                exchange_symbol = f"{symbol}:NASDAQ"
            else:
                exchange_symbol = symbol

            url = f"https://www.google.com/finance/quote/{exchange_symbol.replace(':', ':')}"

            logger.info(f"Fetching {symbol} from Google Finance: {url}")
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                logger.warning(f"Google Finance returned status {response.status_code} for {symbol}")
                return None

            soup = BeautifulSoup(response.text, 'lxml')

            # Google Finance price selectors
            price_selectors = [
                'div.YMlKec.fxKbKc',  # Current price div
                '[data-last-price]',
                'div[jsname="ip75Cb"]',
            ]

            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = self._extract_price(price_text)
                    if price:
                        logger.info(f"Fetched {symbol} from Google Finance: ${price:.2f}")
                        return price

            logger.warning(f"Could not find price element for {symbol} on Google Finance")
            return None

        except Exception as e:
            logger.error(f"Error fetching {symbol} from Google Finance: {str(e)}")
            return None

    def get_price_from_marketwatch(self, symbol: str) -> Optional[float]:
        """
        Fetch stock price from MarketWatch

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')

        Returns:
            Current stock price or None if fetch fails
        """
        try:
            url = f"https://www.marketwatch.com/investing/stock/{symbol.lower()}"

            logger.info(f"Fetching {symbol} from MarketWatch: {url}")
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                logger.warning(f"MarketWatch returned status {response.status_code} for {symbol}")
                return None

            soup = BeautifulSoup(response.text, 'lxml')

            # MarketWatch price selectors
            price_selectors = [
                'bg-quote.value',
                'h3.intraday__price span.value',
                '[class*="LastPrice"]',
            ]

            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = self._extract_price(price_text)
                    if price:
                        logger.info(f"Fetched {symbol} from MarketWatch: ${price:.2f}")
                        return price

            logger.warning(f"Could not find price element for {symbol} on MarketWatch")
            return None

        except Exception as e:
            logger.error(f"Error fetching {symbol} from MarketWatch: {str(e)}")
            return None

    def _extract_price(self, text: str) -> Optional[float]:
        """
        Extract price from text string
        Handles various formats: "175.50", "$175.50", "175,50 EUR", etc.

        Args:
            text: Text containing price

        Returns:
            Extracted price as float or None
        """
        try:
            # Remove currency symbols and extra whitespace
            text = text.strip().replace('$', '').replace('€', '').replace('USD', '').replace('EUR', '')

            # Find numbers with decimals (both . and , as decimal separators)
            # Pattern matches: 123.45, 123,45, 1,234.56, 1.234,56
            matches = re.findall(r'[\d\s]+[.,]\d+|[\d]+', text)

            if not matches:
                return None

            # Take the first match and clean it
            price_str = matches[0].strip()

            # Remove spaces (for numbers like "1 234.56")
            price_str = price_str.replace(' ', '')

            # Handle European format (comma as decimal separator)
            # If there's a comma after the last dot, or only comma, use comma as decimal
            if ',' in price_str and '.' in price_str:
                # Determine which is decimal separator (the last one)
                if price_str.rindex(',') > price_str.rindex('.'):
                    # Comma is decimal separator: "1.234,56" -> "1234.56"
                    price_str = price_str.replace('.', '').replace(',', '.')
                else:
                    # Dot is decimal separator: "1,234.56" -> "1234.56"
                    price_str = price_str.replace(',', '')
            elif ',' in price_str:
                # Only comma: assume it's decimal separator
                price_str = price_str.replace(',', '.')

            return float(price_str)

        except (ValueError, AttributeError) as e:
            logger.debug(f"Could not extract price from '{text}': {str(e)}")
            return None

    def get_stock_price(self, symbol: str, sources: list = None) -> Optional[float]:
        """
        Fetch stock price trying multiple sources in order

        Args:
            symbol: Stock ticker symbol
            sources: List of sources to try (default: all)

        Returns:
            Current stock price or None if all sources fail
        """
        if sources is None:
            sources = ['google', 'marketwatch', 'boursorama']

        for source in sources:
            try:
                if source == 'google':
                    price = self.get_price_from_google_finance(symbol)
                elif source == 'marketwatch':
                    price = self.get_price_from_marketwatch(symbol)
                elif source == 'boursorama':
                    price = self.get_price_from_boursorama(symbol)
                else:
                    logger.warning(f"Unknown source: {source}")
                    continue

                if price is not None:
                    return price

            except Exception as e:
                logger.error(f"Error with source {source} for {symbol}: {str(e)}")
                continue

        logger.error(f"All sources failed for {symbol}")
        return None
