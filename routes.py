import os
import logging
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
from app import app, db
from models import ThesisAnalysis, DocumentUpload, SignalMonitoring, NotificationLog
from services.thesis_analyzer import ThesisAnalyzer
from services.document_processor import DocumentProcessor
from services.signal_extraction import SignalExtractor
from services.notification_service import NotificationService
from config import Config

# Initialize services
thesis_analyzer = ThesisAnalyzer()
document_processor = DocumentProcessor()
signal_extractor = SignalExtractor()
notification_service = NotificationService()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main analysis interface for investment thesis and signal extraction"""
    return render_template('analysis.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Main analysis endpoint for thesis and document processing"""
    try:
        thesis_text = request.form.get('thesis_text')
        focus_primary_signals = request.form.get('focus_primary_signals') == 'on'
        
        if not thesis_text:
            return jsonify({'error': 'Thesis text is required'}), 400
        
        # Process uploaded research files
        processed_documents = []
        research_files = request.files.getlist('research_files')
        
        for file in research_files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
                # Create upload directory if it doesn't exist
                upload_dir = Config.UPLOAD_FOLDER
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                
                # Process the document
                processed_data = document_processor.process_document(file_path)
                processed_documents.append({
                    'filename': filename,
                    'data': processed_data
                })
        
        # Analyze thesis and extract signals
        analysis_result = thesis_analyzer.analyze_thesis(thesis_text)
        
        # Extract signals from documents and thesis using the classification hierarchy
        signals_result = signal_extractor.extract_signals_from_analysis(
            thesis_text, 
            processed_documents, 
            focus_primary=focus_primary_signals
        )
        
        # Combine results
        combined_result = {
            'thesis_analysis': analysis_result,
            'signal_extraction': signals_result,
            'processed_documents': len(processed_documents),
            'focus_primary_signals': focus_primary_signals
        }
        
        return jsonify(combined_result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/thesis/new', methods=['GET', 'POST'])
def new_thesis():
    """Create a new thesis analysis"""
    if request.method == 'POST':
        title = request.form.get('title')
        thesis_text = request.form.get('thesis_text')
        
        if not title or not thesis_text:
            flash('Title and thesis text are required', 'error')
            return render_template('thesis_analysis.html')
        
        try:
            # Analyze the thesis using AI
            analysis_result = thesis_analyzer.analyze_thesis(thesis_text)
            
            # Save to database
            thesis_analysis = ThesisAnalysis(
                title=title,
                original_thesis=thesis_text,
                core_claim=analysis_result.get('core_claim'),
                causal_chain=analysis_result.get('causal_chain'),
                assumptions=analysis_result.get('assumptions'),
                mental_model=analysis_result.get('mental_model'),
                counter_thesis=analysis_result.get('counter_thesis'),
                metrics_to_track=analysis_result.get('metrics_to_track'),
                monitoring_plan=analysis_result.get('monitoring_plan')
            )
            
            db.session.add(thesis_analysis)
            db.session.commit()
            
            # Set up monitoring signals
            if analysis_result.get('metrics_to_track'):
                for metric in analysis_result.get('metrics_to_track', []):
                    signal = SignalMonitoring(
                        thesis_analysis_id=thesis_analysis.id,
                        signal_name=metric.get('name', ''),
                        signal_type=metric.get('type', 'price'),
                        threshold_value=metric.get('threshold'),
                        threshold_type=metric.get('threshold_type', 'change_percent')
                    )
                    db.session.add(signal)
            
            db.session.commit()
            
            flash('Thesis analysis created successfully', 'success')
            return redirect(url_for('view_thesis', id=thesis_analysis.id))
            
        except Exception as e:
            logging.error(f"Error analyzing thesis: {str(e)}")
            flash('Error analyzing thesis. Please try again.', 'error')
            return render_template('thesis_analysis.html')
    
    return render_template('thesis_analysis.html')

@app.route('/thesis/<int:id>')
def view_thesis(id):
    """View a specific thesis analysis"""
    thesis = ThesisAnalysis.query.get_or_404(id)
    signals = SignalMonitoring.query.filter_by(thesis_analysis_id=id).all()
    documents = DocumentUpload.query.filter_by(thesis_analysis_id=id).all()
    
    return render_template('thesis_analysis.html', 
                         thesis=thesis, 
                         signals=signals,
                         documents=documents,
                         view_mode=True)

@app.route('/documents/upload', methods=['GET', 'POST'])
def upload_document():
    """Upload and process research documents"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        thesis_id = request.form.get('thesis_id')
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Create upload directory if it doesn't exist
            upload_dir = Config.UPLOAD_FOLDER
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            try:
                # Process the document
                processed_data = document_processor.process_document(file_path)
                
                # Save document record
                document = DocumentUpload(
                    filename=filename,
                    file_type=filename.rsplit('.', 1)[1].lower(),
                    file_size=os.path.getsize(file_path),
                    upload_path=file_path,
                    processed_data=processed_data,
                    document_metadata={'original_filename': file.filename},
                    thesis_analysis_id=int(thesis_id) if thesis_id else None
                )
                
                db.session.add(document)
                db.session.commit()
                
                flash('Document uploaded and processed successfully', 'success')
                
                if thesis_id:
                    return redirect(url_for('view_thesis', id=thesis_id))
                else:
                    return redirect(url_for('document_list'))
                    
            except Exception as e:
                logging.error(f"Error processing document: {str(e)}")
                flash('Error processing document. Please try again.', 'error')
                # Clean up uploaded file on error
                if os.path.exists(file_path):
                    os.remove(file_path)
        else:
            flash('Invalid file type. Please upload PDF, Excel, or CSV files.', 'error')
    
    # Get list of existing theses for association
    theses = ThesisAnalysis.query.order_by(ThesisAnalysis.created_at.desc()).all()
    return render_template('document_upload.html', theses=theses)

@app.route('/documents')
def document_list():
    """List all uploaded documents"""
    documents = DocumentUpload.query.order_by(DocumentUpload.created_at.desc()).all()
    return render_template('document_upload.html', documents=documents, list_mode=True)

@app.route('/monitoring')
def monitoring_dashboard():
    """Monitoring dashboard showing active signals and notifications"""
    active_signals = SignalMonitoring.query.filter_by(status='active').all()
    triggered_signals = SignalMonitoring.query.filter_by(status='triggered').all()
    recent_notifications = NotificationLog.query.order_by(NotificationLog.sent_at.desc()).limit(10).all()
    
    return render_template('monitoring.html',
                         active_signals=active_signals,
                         triggered_signals=triggered_signals,
                         recent_notifications=recent_notifications)

@app.route('/api/signals/check', methods=['POST'])
def check_signals():
    """API endpoint to manually trigger signal checking"""
    try:
        results = signal_extractor.check_all_signals()
        return jsonify({'status': 'success', 'results': results})
    except Exception as e:
        logging.error(f"Error checking signals: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/notifications/<int:id>/acknowledge', methods=['POST'])
def acknowledge_notification(id):
    """Mark a notification as acknowledged"""
    notification = NotificationLog.query.get_or_404(id)
    notification.acknowledged = True
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/api/thesis/<int:id>/data', methods=['GET'])
def get_thesis_data(id):
    """Get thesis data as JSON for frontend rendering"""
    thesis = ThesisAnalysis.query.get_or_404(id)
    return jsonify(thesis.to_dict())

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
