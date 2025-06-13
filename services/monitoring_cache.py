"""
Monitoring Cache Service for Performance Optimization

Provides cached monitoring data to resolve network connection timeouts
and improve dashboard response times.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from models import ThesisAnalysis, SignalMonitoring, NotificationLog, db


class MonitoringCache:
    """
    Lightweight monitoring cache for fast dashboard loading
    """
    
    def __init__(self):
        self.cache_timeout = 60  # 1 minute cache
        self.last_update = None
        self.cached_data = {}
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get optimized dashboard data with caching
        """
        try:
            # Check cache validity
            if self._is_cache_valid():
                return self.cached_data
            
            # Refresh cache with optimized queries
            self._refresh_cache()
            return self.cached_data
            
        except Exception as e:
            logging.error(f"Monitoring cache error: {str(e)}")
            return self._get_minimal_data()
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if not self.last_update or not self.cached_data:
            return False
        
        cache_age = (datetime.utcnow() - self.last_update).total_seconds()
        return cache_age < self.cache_timeout
    
    def _refresh_cache(self):
        """Refresh cached data with optimized queries"""
        try:
            # Get recent theses with minimal data
            thesis_analyses = db.session.query(
                ThesisAnalysis.id,
                ThesisAnalysis.title,
                ThesisAnalysis.created_at
            ).order_by(ThesisAnalysis.created_at.desc()).limit(20).all()
            
            # Get active signals count only
            active_signals_count = db.session.query(SignalMonitoring.id)\
                .filter(SignalMonitoring.status == 'active').count()
            
            # Get recent notifications count
            recent_notifications_count = db.session.query(NotificationLog.id)\
                .filter(NotificationLog.sent_at >= datetime.utcnow() - timedelta(days=7))\
                .count()
            
            # Cache the data
            self.cached_data = {
                'thesis_analyses': [
                    {
                        'id': t.id,
                        'title': t.title or 'Investment Thesis',
                        'created_at': t.created_at.isoformat() if t.created_at else datetime.utcnow().isoformat()
                    }
                    for t in thesis_analyses
                ],
                'stats': {
                    'total_published': len(thesis_analyses),
                    'active_signals': active_signals_count,
                    'recent_notifications': recent_notifications_count
                },
                'status_distribution': {
                    'active': active_signals_count,
                    'triggered': 0,
                    'inactive': 0
                },
                'active_signals': [],
                'recent_notifications': []
            }
            
            self.last_update = datetime.utcnow()
            logging.info("Monitoring cache refreshed successfully")
            
        except Exception as e:
            logging.error(f"Cache refresh failed: {str(e)}")
            self.cached_data = self._get_minimal_data()
    
    def _get_minimal_data(self) -> Dict[str, Any]:
        """Get minimal data when cache fails"""
        return {
            'thesis_analyses': [],
            'stats': {
                'total_published': 0,
                'active_signals': 0,
                'recent_notifications': 0
            },
            'status_distribution': {
                'active': 0,
                'triggered': 0,
                'inactive': 0
            },
            'active_signals': [],
            'recent_notifications': []
        }
    
    def get_thesis_summary(self, thesis_id: int) -> Dict[str, Any]:
        """Get cached thesis summary for monitoring"""
        try:
            # Get basic thesis data
            thesis = db.session.query(
                ThesisAnalysis.id,
                ThesisAnalysis.title,
                ThesisAnalysis.created_at
            ).filter(ThesisAnalysis.id == thesis_id).first()
            
            if not thesis:
                return {'error': 'Thesis not found'}
            
            # Get signal count for this thesis
            signals_count = db.session.query(SignalMonitoring.id)\
                .filter(SignalMonitoring.thesis_analysis_id == thesis_id)\
                .count()
            
            # Get notifications count
            notifications_count = db.session.query(NotificationLog.id)\
                .join(SignalMonitoring)\
                .filter(SignalMonitoring.thesis_analysis_id == thesis_id)\
                .count()
            
            return {
                'thesis': {
                    'id': thesis.id,
                    'title': thesis.title or 'Investment Thesis',
                    'created_at': thesis.created_at.isoformat() if thesis.created_at else datetime.utcnow().isoformat()
                },
                'signals_count': signals_count,
                'notifications_count': notifications_count
            }
            
        except Exception as e:
            logging.error(f"Thesis summary error: {str(e)}")
            return {'error': 'Failed to load thesis data'}


# Global cache instance
monitoring_cache = MonitoringCache()