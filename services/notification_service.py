import os
import logging
import smtplib
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from config import Config

class NotificationService:
    """
    Service for sending notifications via various channels
    """
    
    def __init__(self):
        self.webhook_url = Config.NOTIFICATION_WEBHOOK_URL
        self.smtp_server = Config.EMAIL_SMTP_SERVER
        self.smtp_port = Config.EMAIL_SMTP_PORT
        self.email_username = Config.EMAIL_USERNAME
        self.email_password = Config.EMAIL_PASSWORD
        
        # Check which notification methods are available
        self.webhook_enabled = bool(self.webhook_url)
        self.email_enabled = bool(self.smtp_server and self.email_username and self.email_password)
        
        if not self.webhook_enabled and not self.email_enabled:
            logging.warning("No notification methods configured")
    
    def send_notification(self, notification_type: str, message: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send notification using available methods
        """
        success = False
        
        # Try webhook first
        if self.webhook_enabled:
            try:
                webhook_success = self._send_webhook_notification(notification_type, message, data)
                if webhook_success:
                    success = True
                    logging.info(f"Webhook notification sent: {notification_type}")
            except Exception as e:
                logging.error(f"Failed to send webhook notification: {str(e)}")
        
        # Try email as backup
        if self.email_enabled:
            try:
                email_success = self._send_email_notification(notification_type, message, data)
                if email_success:
                    success = True
                    logging.info(f"Email notification sent: {notification_type}")
            except Exception as e:
                logging.error(f"Failed to send email notification: {str(e)}")
        
        # Log to console as fallback
        if not success:
            self._log_notification(notification_type, message, data)
            logging.warning(f"Notification logged to console (no other methods available): {notification_type}")
            success = True  # Consider console logging as successful
        
        return success
    
    def _send_webhook_notification(self, notification_type: str, message: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send notification via webhook
        """
        payload = {
            'type': notification_type,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data or {}
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                return True
            else:
                logging.error(f"Webhook returned status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Webhook request failed: {str(e)}")
            return False
    
    def _send_email_notification(self, notification_type: str, message: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send notification via email
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_username
            msg['To'] = self.email_username  # Send to self for now
            msg['Subject'] = f"Investment Thesis Alert: {notification_type}"
            
            # Create email body
            body = self._create_email_body(notification_type, message, data)
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_username, self.email_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            logging.error(f"Email sending failed: {str(e)}")
            return False
    
    def _create_email_body(self, notification_type: str, message: str, data: Optional[Dict[str, Any]] = None) -> str:
        """
        Create HTML email body
        """
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .alert {{ background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .info {{ background-color: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .data {{ background-color: #f8f9fa; padding: 10px; border-radius: 3px; font-family: monospace; }}
                h2 {{ color: #333; }}
                .timestamp {{ color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <h2>Investment Thesis Intelligence System Alert</h2>
            
            <div class="{'alert' if 'alert' in notification_type else 'info'}">
                <h3>Alert Type: {notification_type.replace('_', ' ').title()}</h3>
                <p><strong>Message:</strong> {message}</p>
                <p class="timestamp"><strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
        """
        
        if data:
            html_body += """
            <h3>Additional Data:</h3>
            <div class="data">
            """
            
            for key, value in data.items():
                html_body += f"<p><strong>{key.replace('_', ' ').title()}:</strong> {value}</p>"
            
            html_body += "</div>"
        
        html_body += """
            <hr>
            <p><em>This is an automated notification from the Investment Thesis Intelligence System.</em></p>
        </body>
        </html>
        """
        
        return html_body
    
    def _log_notification(self, notification_type: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Log notification to console as fallback
        """
        log_message = f"NOTIFICATION [{notification_type}]: {message}"
        if data:
            log_message += f" | Data: {data}"
        
        logging.info(log_message)
        print(f"[{datetime.utcnow().isoformat()}] {log_message}")
    
    def send_price_alert(self, symbol: str, current_price: float, change_percent: float, threshold: float) -> bool:
        """
        Send a price change alert
        """
        message = f"Price Alert: {symbol} changed by {change_percent:.2f}% (current: ${current_price:.2f}), exceeding {threshold:.1f}% threshold"
        
        data = {
            'symbol': symbol,
            'current_price': current_price,
            'change_percent': change_percent,
            'threshold': threshold,
            'alert_type': 'price_change'
        }
        
        return self.send_notification('price_alert', message, data)
    
    def send_volume_alert(self, symbol: str, current_volume: int, threshold: int, threshold_type: str) -> bool:
        """
        Send a volume alert
        """
        message = f"Volume Alert: {symbol} volume {current_volume:,} is {threshold_type} threshold {threshold:,}"
        
        data = {
            'symbol': symbol,
            'current_volume': current_volume,
            'threshold': threshold,
            'threshold_type': threshold_type,
            'alert_type': 'volume'
        }
        
        return self.send_notification('volume_alert', message, data)
    
    def send_thesis_analysis_complete(self, thesis_title: str, thesis_id: int) -> bool:
        """
        Send notification when thesis analysis is complete
        """
        message = f"Thesis analysis completed: '{thesis_title}' (ID: {thesis_id})"
        
        data = {
            'thesis_title': thesis_title,
            'thesis_id': thesis_id,
            'alert_type': 'analysis_complete'
        }
        
        return self.send_notification('analysis_complete', message, data)
    
    def send_document_processed(self, filename: str, document_type: str, thesis_id: Optional[int] = None) -> bool:
        """
        Send notification when document processing is complete
        """
        message = f"Document processed: {filename} ({document_type})"
        if thesis_id:
            message += f" - linked to thesis ID {thesis_id}"
        
        data = {
            'filename': filename,
            'document_type': document_type,
            'thesis_id': thesis_id,
            'alert_type': 'document_processed'
        }
        
        return self.send_notification('document_processed', message, data)
    
    def test_notification_methods(self) -> Dict[str, bool]:
        """
        Test all configured notification methods
        """
        results = {}
        
        test_message = "Test notification from Investment Thesis Intelligence System"
        test_data = {
            'test': True,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if self.webhook_enabled:
            try:
                results['webhook'] = self._send_webhook_notification('test', test_message, test_data)
            except Exception as e:
                results['webhook'] = False
                logging.error(f"Webhook test failed: {str(e)}")
        else:
            results['webhook'] = False
        
        if self.email_enabled:
            try:
                results['email'] = self._send_email_notification('test', test_message, test_data)
            except Exception as e:
                results['email'] = False
                logging.error(f"Email test failed: {str(e)}")
        else:
            results['email'] = False
        
        # Console logging always works
        results['console'] = True
        self._log_notification('test', test_message, test_data)
        
        return results
    
    def get_notification_status(self) -> Dict[str, Any]:
        """
        Get status of notification service
        """
        return {
            'webhook_enabled': self.webhook_enabled,
            'webhook_url': self.webhook_url if self.webhook_enabled else None,
            'email_enabled': self.email_enabled,
            'email_server': self.smtp_server if self.email_enabled else None,
            'console_enabled': True
        }
