"""
Threshold Checker Module
Checks if stock prices have crossed defined thresholds
"""
import os
from typing import Dict, List, Optional
import logging

import pymysql
import pymysql.cursors

logger = logging.getLogger(__name__)


class ThresholdChecker:
    """Manages stock thresholds and checks for threshold violations"""

    def __init__(self):
        self._db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME'),
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor,
        }
        self.stocks = self._query_stocks()

    def _query_stocks(self) -> List[Dict]:
        """Query active (unsold) stocks from the database"""
        try:
            conn = pymysql.connect(**self._db_config)
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT * FROM stocks WHERE sold = 0 ORDER BY initial_date, id"
                    )
                    rows = cursor.fetchall()

            stocks = []
            for row in rows:
                stock = {
                    'symbol': row['symbol'],
                    'name': row['name'],
                    'sector': row['sector'],
                    'currency': row['currency'],
                    'initial_value': float(row['initial_value']),
                    'initial_quantity': row['initial_quantity'],
                    'initial_date': row['initial_date'].strftime('%Y-%m-%d') if row['initial_date'] else None,
                    'upper_threshold': float(row['upper_threshold']),
                    'lower_threshold': float(row['lower_threshold']),
                }
                if row['purchase_fee'] is not None:
                    stock['purchase_fee'] = float(row['purchase_fee'])
                stocks.append(stock)

            logger.info(f"Loaded {len(stocks)} stocks from database")
            return stocks
        except Exception as e:
            logger.error(f"Error loading stocks from database: {e}")
            return []

    def reload_if_changed(self) -> bool:
        """
        Re-query the database and update the stock list.

        Returns:
            True if the number of tracked stocks changed, False otherwise
        """
        new_stocks = self._query_stocks()
        changed = len(new_stocks) != len(self.stocks)
        self.stocks = new_stocks
        return changed

    def check_thresholds(self, prices: Dict[str, Optional[float]]) -> List[Dict]:
        """
        Check if any stock prices have crossed their thresholds

        Args:
            prices: Dictionary mapping stock symbols to current prices

        Returns:
            List of threshold violations with details

        Note:
            - Set threshold to -1 to disable that threshold check
            - Set threshold to None or omit it to disable that threshold check
        """
        violations = []

        for stock_config in self.stocks:
            symbol = stock_config.get('symbol')
            name = stock_config.get('name', '')
            currency = stock_config.get('currency', 'EUR')
            upper_threshold = stock_config.get('upper_threshold')
            lower_threshold = stock_config.get('lower_threshold')

            # Create display name (show name if available, otherwise just symbol)
            display_name = f"{name} ({symbol})" if name else symbol

            if symbol not in prices or prices[symbol] is None:
                logger.warning(f"No price data for {display_name}")
                continue

            current_price = prices[symbol]

            # Check upper threshold
            # Skip if threshold is None, 0, or -1 (disabled)
            if upper_threshold is not None and upper_threshold > 0 and current_price >= upper_threshold:
                violations.append({
                    'symbol': symbol,
                    'name': name,
                    'display_name': display_name,
                    'current_price': current_price,
                    'currency': currency,
                    'threshold': upper_threshold,
                    'threshold_type': 'upper',
                    'message': f"{display_name} reached {current_price:.4f} {currency} (threshold: {upper_threshold:.4f} {currency})"
                })
                logger.info(f"Upper threshold violation: {display_name} at {current_price:.4f} {currency}")

            # Check lower threshold
            # Skip if threshold is None, 0, or -1 (disabled)
            if lower_threshold is not None and lower_threshold > 0 and current_price <= lower_threshold:
                violations.append({
                    'symbol': symbol,
                    'name': name,
                    'display_name': display_name,
                    'current_price': current_price,
                    'currency': currency,
                    'threshold': lower_threshold,
                    'threshold_type': 'lower',
                    'message': f"{display_name} dropped to {current_price:.4f} {currency} (threshold: {lower_threshold:.4f} {currency})"
                })
                logger.info(f"Lower threshold violation: {display_name} at {current_price:.4f} {currency}")

        return violations

    def get_tracked_symbols(self) -> List[str]:
        """Get list of all tracked stock symbols"""
        return [stock.get('symbol') for stock in self.stocks if stock.get('symbol')]

    def get_stock_display_names(self) -> List[str]:
        """Get list of display names (name + symbol or just symbol)"""
        display_names = []
        for stock in self.stocks:
            symbol = stock.get('symbol')
            name = stock.get('name', '')
            if symbol:
                display_names.append(f"{name} ({symbol})" if name else symbol)
        return display_names

    def get_symbol_to_name_map(self) -> Dict[str, str]:
        """Get mapping of symbol to name for display purposes"""
        return {stock.get('symbol'): stock.get('name', '') for stock in self.stocks if stock.get('symbol')}
