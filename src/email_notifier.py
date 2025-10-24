"""
Email Notifier Module
Sends email alerts when stock thresholds are crossed
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
import logging
import os

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Sends email notifications for threshold violations"""

    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')

    def send_alert(self, violations: List[Dict]) -> bool:
        """
        Send email alert for threshold violations

        Args:
            violations: List of threshold violation dictionaries

        Returns:
            True if email sent successfully, False otherwise
        """
        if not violations:
            logger.info("No violations to report")
            return True

        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            logger.error("Email configuration incomplete. Check environment variables.")
            return False

        try:
            # Create email message
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = self.recipient_email
            message['Subject'] = f'Stock Alert: {len(violations)} Threshold(s) Crossed'

            # Build email body
            body = self._build_email_body(violations)
            message.attach(MIMEText(body, 'plain'))

            # Send email
            # Use SMTP_SSL for port 465, regular SMTP with STARTTLS for port 587
            if self.smtp_port == 465:
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(message)
            else:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(message)

            logger.info(f"Alert email sent successfully for {len(violations)} violation(s)")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def _build_email_body(self, violations: List[Dict]) -> str:
        """Build the email body text from violations"""
        body = "Stock Threshold Alert\n"
        body += "=" * 50 + "\n\n"

        for violation in violations:
            # Show name if available
            if violation.get('name'):
                body += f"Stock: {violation['name']}\n"
                body += f"Symbol: {violation['symbol']}\n"
            else:
                body += f"Symbol: {violation['symbol']}\n"

            body += f"Current Price: {violation['current_price']:.4f}€\n"
            body += f"Threshold ({violation['threshold_type']}): {violation['threshold']:.4f}€\n"
            body += f"Status: {violation['message']}\n"
            body += "-" * 50 + "\n\n"

        body += "\nThis is an automated alert from StockTracker.\n"
        return body

    def send_daily_summary(self, stocks_data: List[Dict]) -> bool:
        """
        Send daily summary email with all stock prices and thresholds

        Args:
            stocks_data: List of dictionaries with stock info (symbol, name, price, thresholds)

        Returns:
            True if email sent successfully, False otherwise
        """
        if not stocks_data:
            logger.info("No stocks data to report in daily summary")
            return True

        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            logger.error("Email configuration incomplete. Check environment variables.")
            return False

        try:
            # Create email message
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = self.recipient_email
            message['Subject'] = 'Stock Price Summary - Daily Report'

            # Build HTML email body
            html_body = self._build_summary_html(stocks_data)
            message.attach(MIMEText(html_body, 'html'))

            # Send email
            # Use SMTP_SSL for port 465, regular SMTP with STARTTLS for port 587
            if self.smtp_port == 465:
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(message)
            else:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(message)

            logger.info(f"Daily summary email sent successfully for {len(stocks_data)} stock(s)")
            return True

        except Exception as e:
            logger.error(f"Failed to send daily summary email: {str(e)}")
            return False

    def _build_summary_body(self, stocks_data: List[Dict]) -> str:
        """Build the email body text for daily summary"""
        body = "Stock Price Summary - Daily Report\n"
        body += "=" * 50 + "\n\n"

        for stock in stocks_data:
            # Show name and symbol
            if stock.get('name'):
                body += f"Stock: {stock['name']}\n"
                body += f"Symbol: {stock['symbol']}\n"
            else:
                body += f"Symbol: {stock['symbol']}\n"

            # Current price
            price = stock.get('price')
            if price is not None:
                body += f"Current Price: {price:.4f}€\n"
            else:
                body += "Current Price: N/A\n"

            # Thresholds
            upper = stock.get('upper_threshold')
            lower = stock.get('lower_threshold')

            if upper and upper > 0:
                body += f"Upper Threshold: {upper:.4f}€\n"
            else:
                body += "Upper Threshold: Not set\n"

            if lower and lower > 0:
                body += f"Lower Threshold: {lower:.4f}€\n"
            else:
                body += "Lower Threshold: Not set\n"

            # Status
            if price is not None:
                status = "OK"
                if upper and upper > 0 and price >= upper:
                    status = "ALERT - Above upper threshold"
                elif lower and lower > 0 and price <= lower:
                    status = "ALERT - Below lower threshold"
                body += f"Status: {status}\n"

            body += "-" * 50 + "\n\n"

        body += "\nThis is an automated daily summary from StockTracker.\n"
        return body

    def _build_summary_html(self, stocks_data: List[Dict]) -> str:
        """Build HTML email body for daily summary with colored lines"""
        html = """
        <html>
        <head>
            <style>
                body { font-family: 'Courier New', monospace; font-size: 14px; }
                .header { font-weight: bold; font-size: 16px; margin-bottom: 20px; }
                .stock-ok { color: #0066cc; margin: 5px 0; }
                .stock-alert { color: #cc0000; margin: 5px 0; }
                .footer { margin-top: 20px; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="header">Stock Price Summary - Daily Report</div>
        """

        for stock in stocks_data:
            # Get stock info
            name = stock.get('name', '')
            symbol = stock.get('symbol')
            price = stock.get('price')
            upper = stock.get('upper_threshold')
            lower = stock.get('lower_threshold')

            # Build display name
            display_name = f"{name} ({symbol})" if name else symbol

            # Format thresholds
            upper_text = f"{upper:.4f}€" if (upper and upper > 0) else "Not set"
            lower_text = f"{lower:.4f}€" if (lower and lower > 0) else "Not set"

            # Determine status and color
            is_alert = False
            if price is not None:
                if upper and upper > 0 and price >= upper:
                    is_alert = True
                elif lower and lower > 0 and price <= lower:
                    is_alert = True

            # Build line
            if price is not None:
                price_text = f"{price:.4f}€"
                status_text = "[ALERT]" if is_alert else "[OK]"
                css_class = "stock-alert" if is_alert else "stock-ok"

                html += f'<div class="{css_class}">{display_name}: {price_text} {status_text} (Upper: {upper_text}, Lower: {lower_text})</div>\n'
            else:
                html += f'<div class="stock-ok">{display_name}: N/A (Upper: {upper_text}, Lower: {lower_text})</div>\n'

        html += """
            <div class="footer">This is an automated daily summary from StockTracker.</div>
        </body>
        </html>
        """

        return html
