import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app import db
from models import SignalMonitoring, NotificationLog
from services.data_registry import DataRegistry
from services.notification_service import NotificationService
from config import Config

class SignalExtractor:
    """
    Service for extracting and monitoring signals from market data
    """
    
    def __init__(self):
        self.data_registry = DataRegistry()
        self.notification_service = NotificationService()
        self.price_change_threshold = Config.PRICE_CHANGE_THRESHOLD
    
    def check_all_signals(self) -> List[Dict[str, Any]]:
        """
        Check all active signals for threshold breaches
        """
        active_signals = SignalMonitoring.query.filter_by(status='active').all()
        results = []
        
        for signal in active_signals:
            try:
                result = self._check_signal(signal)
                results.append(result)
                
                # Update last checked timestamp
                signal.last_checked = datetime.utcnow()
                db.session.commit()
                
            except Exception as e:
                logging.error(f"Error checking signal {signal.id}: {str(e)}")
                results.append({
                    'signal_id': signal.id,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    def _check_signal(self, signal: SignalMonitoring) -> Dict[str, Any]:
        """
        Check a specific signal for threshold breach
        """
        try:
            # Extract the asset symbol or identifier from signal name
            symbol = self._extract_symbol_from_signal(signal.signal_name)
            
            if signal.signal_type == 'price':
                return self._check_price_signal(signal, symbol)
            elif signal.signal_type == 'volume':
                return self._check_volume_signal(signal, symbol)
            elif signal.signal_type == 'sentiment':
                return self._check_sentiment_signal(signal, symbol)
            elif signal.signal_type == 'economic':
                return self._check_economic_signal(signal, symbol)
            else:
                return {
                    'signal_id': signal.id,
                    'status': 'unsupported',
                    'message': f"Signal type '{signal.signal_type}' not supported"
                }
                
        except Exception as e:
            logging.error(f"Error checking signal {signal.id}: {str(e)}")
            return {
                'signal_id': signal.id,
                'status': 'error',
                'error': str(e)
            }
    
    def _check_price_signal(self, signal: SignalMonitoring, symbol: str) -> Dict[str, Any]:
        """
        Check price-based signals
        """
        # Get current price data
        current_data = self.data_registry.get_asset_data(symbol, 'price')
        
        if not current_data or current_data.get('price') is None:
            return {
                'signal_id': signal.id,
                'status': 'no_data',
                'message': f"No price data available for {symbol}"
            }
        
        current_price = float(current_data['price'])
        change_percent = float(current_data.get('change_percent', 0))
        
        # Update current value
        signal.current_value = current_price
        
        # Check threshold based on type
        triggered = False
        if signal.threshold_type == 'above' and current_price > signal.threshold_value:
            triggered = True
        elif signal.threshold_type == 'below' and current_price < signal.threshold_value:
            triggered = True
        elif signal.threshold_type == 'change_percent' and abs(change_percent) > signal.threshold_value:
            triggered = True
        
        if triggered:
            # Create notification
            notification_data = {
                'symbol': symbol,
                'current_price': current_price,
                'change_percent': change_percent,
                'threshold': signal.threshold_value,
                'threshold_type': signal.threshold_type
            }
            
            message = self._create_price_alert_message(notification_data)
            
            # Save notification
            notification = NotificationLog(
                signal_monitoring_id=signal.id,
                notification_type='price_alert',
                message=message,
                data_snapshot=notification_data
            )
            
            db.session.add(notification)
            
            # Update signal status
            signal.status = 'triggered'
            
            # Send notification
            try:
                self.notification_service.send_notification(
                    notification_type='price_alert',
                    message=message,
                    data=notification_data
                )
            except Exception as e:
                logging.error(f"Failed to send notification: {str(e)}")
            
            db.session.commit()
            
            return {
                'signal_id': signal.id,
                'status': 'triggered',
                'message': message,
                'current_value': current_price,
                'threshold_value': signal.threshold_value
            }
        
        return {
            'signal_id': signal.id,
            'status': 'normal',
            'current_value': current_price,
            'threshold_value': signal.threshold_value
        }
    
    def _check_volume_signal(self, signal: SignalMonitoring, symbol: str) -> Dict[str, Any]:
        """
        Check volume-based signals
        """
        current_data = self.data_registry.get_asset_data(symbol, 'market_data')
        
        if not current_data or current_data.get('volume') is None:
            return {
                'signal_id': signal.id,
                'status': 'no_data',
                'message': f"No volume data available for {symbol}"
            }
        
        current_volume = float(current_data['volume'])
        signal.current_value = current_volume
        
        triggered = False
        if signal.threshold_type == 'above' and current_volume > signal.threshold_value:
            triggered = True
        elif signal.threshold_type == 'below' and current_volume < signal.threshold_value:
            triggered = True
        
        if triggered:
            notification_data = {
                'symbol': symbol,
                'current_volume': current_volume,
                'threshold': signal.threshold_value,
                'threshold_type': signal.threshold_type
            }
            
            message = f"Volume alert for {symbol}: Current volume {current_volume:,.0f} is {signal.threshold_type} threshold {signal.threshold_value:,.0f}"
            
            notification = NotificationLog(
                signal_monitoring_id=signal.id,
                notification_type='volume_alert',
                message=message,
                data_snapshot=notification_data
            )
            
            db.session.add(notification)
            signal.status = 'triggered'
            
            try:
                self.notification_service.send_notification(
                    notification_type='volume_alert',
                    message=message,
                    data=notification_data
                )
            except Exception as e:
                logging.error(f"Failed to send notification: {str(e)}")
            
            db.session.commit()
            
            return {
                'signal_id': signal.id,
                'status': 'triggered',
                'message': message,
                'current_value': current_volume
            }
        
        return {
            'signal_id': signal.id,
            'status': 'normal',
            'current_value': current_volume
        }
    
    def _check_sentiment_signal(self, signal: SignalMonitoring, symbol: str) -> Dict[str, Any]:
        """
        Check sentiment-based signals (placeholder for future implementation)
        """
        return {
            'signal_id': signal.id,
            'status': 'not_implemented',
            'message': 'Sentiment analysis not yet implemented'
        }
    
    def _check_economic_signal(self, signal: SignalMonitoring, symbol: str) -> Dict[str, Any]:
        """
        Check economic indicator signals (placeholder for future implementation)
        """
        return {
            'signal_id': signal.id,
            'status': 'not_implemented',
            'message': 'Economic indicator monitoring not yet implemented'
        }
    
    def _extract_symbol_from_signal(self, signal_name: str) -> str:
        """
        Extract trading symbol from signal name
        """
        # Simple extraction - in practice this would be more sophisticated
        # Look for common patterns like "NVDA price" or "AAPL volume"
        words = signal_name.upper().split()
        
        # Common stock symbols are typically 1-5 characters
        for word in words:
            if len(word) <= 5 and word.isalpha():
                return word
        
        # If no symbol found, return the first word
        return words[0] if words else signal_name
    
    def _create_price_alert_message(self, data: Dict[str, Any]) -> str:
        """
        Create a formatted price alert message
        """
        symbol = data['symbol']
        current_price = data['current_price']
        change_percent = data['change_percent']
        threshold = data['threshold']
        threshold_type = data['threshold_type']
        
        if threshold_type == 'change_percent':
            return (f"Price Alert: {symbol} changed by {change_percent:.2f}% "
                   f"(current: ${current_price:.2f}), exceeding {threshold:.1f}% threshold")
        elif threshold_type == 'above':
            return (f"Price Alert: {symbol} price ${current_price:.2f} "
                   f"exceeded threshold of ${threshold:.2f}")
        elif threshold_type == 'below':
            return (f"Price Alert: {symbol} price ${current_price:.2f} "
                   f"fell below threshold of ${threshold:.2f}")
        else:
            return (f"Price Alert: {symbol} triggered at ${current_price:.2f} "
                   f"(change: {change_percent:.2f}%)")
    
    def get_signal_status(self, signal_id: int) -> Dict[str, Any]:
        """
        Get current status of a specific signal
        """
        signal = SignalMonitoring.query.get(signal_id)
        if not signal:
            return {'error': 'Signal not found'}
        
        return {
            'signal_id': signal.id,
            'signal_name': signal.signal_name,
            'signal_type': signal.signal_type,
            'current_value': signal.current_value,
            'threshold_value': signal.threshold_value,
            'threshold_type': signal.threshold_type,
            'status': signal.status,
            'last_checked': signal.last_checked.isoformat() if signal.last_checked else None
        }
    
    def create_signal(self, thesis_analysis_id: int, signal_config: Dict[str, Any]) -> SignalMonitoring:
        """
        Create a new signal for monitoring
        """
        signal = SignalMonitoring(
            thesis_analysis_id=thesis_analysis_id,
            signal_name=signal_config['name'],
            signal_type=signal_config['type'],
            threshold_value=signal_config['threshold'],
            threshold_type=signal_config.get('threshold_type', 'change_percent'),
            status='active'
        )
        
        db.session.add(signal)
        db.session.commit()
        
        logging.info(f"Created new signal: {signal.signal_name} (ID: {signal.id})")
        return signal
    
    def update_signal_threshold(self, signal_id: int, new_threshold: float) -> bool:
        """
        Update the threshold value for a signal
        """
        signal = SignalMonitoring.query.get(signal_id)
        if not signal:
            return False
        
        old_threshold = signal.threshold_value
        signal.threshold_value = new_threshold
        db.session.commit()
        
        logging.info(f"Updated signal {signal_id} threshold from {old_threshold} to {new_threshold}")
        return True
    
    def deactivate_signal(self, signal_id: int) -> bool:
        """
        Deactivate a signal
        """
        signal = SignalMonitoring.query.get(signal_id)
        if not signal:
            return False
        
        signal.status = 'inactive'
        db.session.commit()
        
        logging.info(f"Deactivated signal {signal_id}: {signal.signal_name}")
        return True
