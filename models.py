from app import db
from datetime import datetime
from sqlalchemy import Text, JSON
import json

class ThesisAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    original_thesis = db.Column(Text, nullable=False)
    core_claim = db.Column(Text)
    core_analysis = db.Column(Text)
    causal_chain = db.Column(JSON)
    assumptions = db.Column(JSON)
    mental_model = db.Column(db.String(255))
    counter_thesis = db.Column(JSON)
    metrics_to_track = db.Column(JSON)
    monitoring_plan = db.Column(JSON)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'original_thesis': self.original_thesis,
            'core_claim': self.core_claim,
            'core_analysis': self.core_analysis,
            'causal_chain': self.causal_chain,
            'assumptions': self.assumptions,
            'mental_model': self.mental_model,
            'counter_thesis': self.counter_thesis,
            'metrics_to_track': self.metrics_to_track,
            'monitoring_plan': self.monitoring_plan,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DocumentUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer)
    upload_path = db.Column(db.String(500))
    processed_data = db.Column(JSON)
    document_metadata = db.Column(JSON)
    thesis_analysis_id = db.Column(db.Integer, db.ForeignKey('thesis_analysis.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    thesis_analysis = db.relationship('ThesisAnalysis', backref='documents')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'processed_data': self.processed_data,
            'document_metadata': self.document_metadata,
            'thesis_analysis_id': self.thesis_analysis_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SignalMonitoring(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thesis_analysis_id = db.Column(db.Integer, db.ForeignKey('thesis_analysis.id'), nullable=False)
    signal_name = db.Column(db.String(255), nullable=False)
    signal_type = db.Column(db.String(100), nullable=False)
    current_value = db.Column(db.Float)
    threshold_value = db.Column(db.Float)
    threshold_type = db.Column(db.String(50))  # 'above', 'below', 'change_percent'
    status = db.Column(db.String(50), default='active')  # 'active', 'triggered', 'inactive'
    last_checked = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    thesis_analysis = db.relationship('ThesisAnalysis', backref='signals')
    
    def to_dict(self):
        return {
            'id': self.id,
            'thesis_analysis_id': self.thesis_analysis_id,
            'signal_name': self.signal_name,
            'signal_type': self.signal_type,
            'current_value': self.current_value,
            'threshold_value': self.threshold_value,
            'threshold_type': self.threshold_type,
            'status': self.status,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class NotificationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    signal_monitoring_id = db.Column(db.Integer, db.ForeignKey('signal_monitoring.id'), nullable=False)
    notification_type = db.Column(db.String(100), nullable=False)
    message = db.Column(Text, nullable=False)
    data_snapshot = db.Column(JSON)
    sent_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    acknowledged = db.Column(db.Boolean, default=False)
    
    signal_monitoring = db.relationship('SignalMonitoring', backref='notifications')
    
    def to_dict(self):
        return {
            'id': self.id,
            'signal_monitoring_id': self.signal_monitoring_id,
            'notification_type': self.notification_type,
            'message': self.message,
            'data_snapshot': self.data_snapshot,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'acknowledged': self.acknowledged
        }


class DocumentValidation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    extracted_thesis = db.Column(Text, nullable=False)
    key_findings = db.Column(JSON)
    investment_logic = db.Column(Text)
    risk_factors = db.Column(JSON)
    target_metrics = db.Column(JSON)
    document_summary = db.Column(Text)
    confidence_score = db.Column(db.Float, default=0.0)
    
    # Analysis results
    thesis_analysis_id = db.Column(db.Integer, db.ForeignKey('thesis_analysis.id'))
    validation_report = db.Column(JSON)
    analyst_report = db.Column(Text)
    
    # Status tracking
    status = db.Column(db.String(50), default='pending')  # pending, validated, reviewed
    analyst_feedback = db.Column(Text)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    thesis_analysis = db.relationship('ThesisAnalysis', backref='validations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'extracted_thesis': self.extracted_thesis,
            'key_findings': self.key_findings,
            'investment_logic': self.investment_logic,
            'risk_factors': self.risk_factors,
            'target_metrics': self.target_metrics,
            'document_summary': self.document_summary,
            'confidence_score': self.confidence_score,
            'thesis_analysis_id': self.thesis_analysis_id,
            'validation_report': self.validation_report,
            'status': self.status,
            'analyst_feedback': self.analyst_feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
