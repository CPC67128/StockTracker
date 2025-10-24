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

            body += f"Current Price: €{violation['current_price']:.4f}\n"
            body += f"Threshold ({violation['threshold_type']}): €{violation['threshold']:.4f}\n"
            body += f"Status: {violation['message']}\n"
            body += "-" * 50 + "\n\n"

        body += "\nThis is an automated alert from StockTracker.\n"
        return body
