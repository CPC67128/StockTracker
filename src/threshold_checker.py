"""
Threshold Checker Module
Checks if stock prices have crossed defined thresholds
"""
import json
import os
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ThresholdChecker:
    """Manages stock thresholds and checks for threshold violations"""

    def __init__(self, config_path: str = "config/stocks.json"):
        self.config_path = config_path
        self.last_modified_time = None
        self.stocks = self.load_stocks()

    def load_stocks(self) -> List[Dict]:
        """Load stock threshold configuration from JSON file"""
        if not os.path.exists(self.config_path):
            logger.warning(f"Config file not found: {self.config_path}")
            return []

        try:
            # Update last modified time
            self.last_modified_time = os.path.getmtime(self.config_path)

            with open(self.config_path, 'r') as f:
                data = json.load(f)
                stocks = data.get('stocks', [])
                logger.info(f"Loaded {len(stocks)} stocks from configuration")
                return stocks
        except Exception as e:
            logger.error(f"Error loading stock config: {str(e)}")
            return []

    def check_for_config_changes(self) -> bool:
        """
        Check if the configuration file has been modified since last load

        Returns:
            True if config file has changed, False otherwise
        """
        if not os.path.exists(self.config_path):
            return False

        try:
            current_modified_time = os.path.getmtime(self.config_path)
            if self.last_modified_time is None or current_modified_time > self.last_modified_time:
                return True
            return False
        except Exception as e:
            logger.error(f"Error checking config file modification time: {str(e)}")
            return False

    def reload_if_changed(self) -> bool:
        """
        Reload configuration if file has been modified

        Returns:
            True if configuration was reloaded, False otherwise
        """
        if self.check_for_config_changes():
            logger.info(f"Configuration file changed, reloading stocks from {self.config_path}")
            self.stocks = self.load_stocks()
            return True
        return False

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
