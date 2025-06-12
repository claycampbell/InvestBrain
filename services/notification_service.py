import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
import requests
from datetime import datetime
from config import Config

class NotificationService:
    """
    Service for sending notifications when signals are triggered
    """
    
    def __init__(self):
        self.config = Config()
        self.enabled_channels = self._determine_enabled_channels()
    
    def _determine_enabled_channels(self) -> List[str]:
        """Determine which notification channels are available"""
        channels = []
        
        # Check webhook availability
        if self.config.NOTIFICATION_WEBHOOK_URL:
            channels.append('webhook')
        
        # Check email availability
        if (self.config.EMAIL_SMTP_SERVER and 
            self.config.EMAIL_USERNAME and 
            self.config.EMAIL_PASSWORD):
            channels.append('email')
        
        return channels
    
    def send_signal_notification(self, signal_data: Dict[str, Any], thesis_data: Dict[str, Any]) -> bool:
        """
        Send notification when a signal is triggered
        """
        try:
            notification_sent = False
            
            # Prepare notification content
            message_data = self._prepare_notification_message(signal_data, thesis_data)
            
            # Send via available channels
            for channel in self.enabled_channels:
                try:
                    if channel == 'webhook':
                        if self._send_webhook_notification(message_data):
                            notification_sent = True
                    elif channel == 'email':
                        if self._send_email_notification(message_data):
                            notification_sent = True
                except Exception as e:
                    logging.error(f"Failed to send notification via {channel}: {str(e)}")
            
            return notification_sent
            
        except Exception as e:
            logging.error(f"Error sending signal notification: {str(e)}")
            return False
    
    def _prepare_notification_message(self, signal_data: Dict[str, Any], thesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare notification message content
        """
        return {
            'title': f"Signal Triggered: {signal_data.get('signal_name', 'Unknown Signal')}",
            'message': f"Signal '{signal_data.get('signal_name')}' has been triggered for thesis '{thesis_data.get('title', 'Unknown Thesis')}'",
            'signal_name': signal_data.get('signal_name'),
            'signal_type': signal_data.get('signal_type'),
            'current_value': signal_data.get('current_value'),
            'threshold_value': signal_data.get('threshold_value'),
            'thesis_title': thesis_data.get('title'),
            'thesis_id': thesis_data.get('id'),
            'timestamp': datetime.utcnow().isoformat(),
            'urgency': self._determine_urgency(signal_data)
        }
    
    def _determine_urgency(self, signal_data: Dict[str, Any]) -> str:
        """
        Determine notification urgency based on signal characteristics
        """
        signal_type = signal_data.get('signal_type', '').lower()
        
        if signal_type in ['economic', 'sector']:
            return 'high'
        elif signal_type in ['company', 'technical']:
            return 'medium'
        else:
            return 'low'
    
    def _send_webhook_notification(self, message_data: Dict[str, Any]) -> bool:
        """
        Send notification via webhook
        """
        try:
            webhook_url = self.config.NOTIFICATION_WEBHOOK_URL
            if not webhook_url:
                return False
            
            payload = {
                'text': message_data['title'],
                'attachments': [{
                    'color': 'warning' if message_data['urgency'] == 'high' else 'good',
                    'fields': [
                        {
                            'title': 'Signal',
                            'value': message_data['signal_name'],
                            'short': True
                        },
                        {
                            'title': 'Thesis',
                            'value': message_data['thesis_title'],
                            'short': True
                        },
                        {
                            'title': 'Current Value',
                            'value': str(message_data.get('current_value', 'N/A')),
                            'short': True
                        },
                        {
                            'title': 'Threshold',
                            'value': str(message_data.get('threshold_value', 'N/A')),
                            'short': True
                        }
                    ],
                    'footer': 'Thesis Intelligence System',
                    'ts': message_data['timestamp']
                }]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logging.info(f"Webhook notification sent successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send webhook notification: {str(e)}")
            return False
    
    def _send_email_notification(self, message_data: Dict[str, Any]) -> bool:
        """
        Send notification via email
        """
        try:
            if not all([self.config.EMAIL_SMTP_SERVER, 
                       self.config.EMAIL_USERNAME, 
                       self.config.EMAIL_PASSWORD]):
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.EMAIL_USERNAME
            msg['To'] = self.config.EMAIL_USERNAME  # Send to self for now
            msg['Subject'] = message_data['title']
            
            # Create email body
            body = f"""
Signal Alert: {message_data['signal_name']}

Thesis: {message_data['thesis_title']}
Signal Type: {message_data['signal_type']}
Current Value: {message_data.get('current_value', 'N/A')}
Threshold Value: {message_data.get('threshold_value', 'N/A')}
Urgency: {message_data['urgency']}
Timestamp: {message_data['timestamp']}

This is an automated notification from the Thesis Intelligence System.
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.config.EMAIL_SMTP_SERVER, self.config.EMAIL_SMTP_PORT)
            server.starttls()
            server.login(self.config.EMAIL_USERNAME, self.config.EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            logging.info(f"Email notification sent successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email notification: {str(e)}")
            return False
    
    def test_notification_channels(self) -> Dict[str, bool]:
        """
        Test all configured notification channels
        """
        results = {}
        
        test_message = {
            'title': 'Test Notification',
            'message': 'Testing notification system',
            'signal_name': 'Test Signal',
            'signal_type': 'test',
            'current_value': 100,
            'threshold_value': 90,
            'thesis_title': 'Test Thesis',
            'thesis_id': 1,
            'timestamp': datetime.utcnow().isoformat(),
            'urgency': 'low'
        }
        
        for channel in self.enabled_channels:
            try:
                if channel == 'webhook':
                    results[channel] = self._send_webhook_notification(test_message)
                elif channel == 'email':
                    results[channel] = self._send_email_notification(test_message)
                else:
                    results[channel] = False
            except Exception as e:
                logging.error(f"Error testing {channel}: {str(e)}")
                results[channel] = False
        
        return results
    
    def get_notification_status(self) -> Dict[str, Any]:
        """
        Get status of notification service
        """
        return {
            'enabled_channels': self.enabled_channels,
            'webhook_configured': bool(self.config.NOTIFICATION_WEBHOOK_URL),
            'email_configured': bool(self.config.EMAIL_SMTP_SERVER and 
                                   self.config.EMAIL_USERNAME and 
                                   self.config.EMAIL_PASSWORD),
            'total_channels': len(self.enabled_channels)
        }