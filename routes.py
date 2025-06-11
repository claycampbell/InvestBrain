import os
import logging
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
from app import app, db
from models import ThesisAnalysis, DocumentUpload, SignalMonitoring, NotificationLog
from services.thesis_analyzer import ThesisAnalyzer
from services.document_processor import DocumentProcessor
from services.signal_classifier import SignalClassifier
from services.notification_service import NotificationService
from config import Config

# Initialize services
thesis_analyzer = ThesisAnalyzer()
document_processor = DocumentProcessor()
signal_classifier = SignalClassifier()
notification_service = NotificationService()

def save_thesis_analysis(thesis_text, analysis_result, signals_result):
    """Save completed analysis to database for monitoring"""
    try:
        # Create thesis record
        thesis_analysis = ThesisAnalysis(
            title=analysis_result.get('core_claim', 'Untitled Thesis')[:255],
            original_thesis=thesis_text,
            core_claim=analysis_result.get('core_claim', ''),
            core_analysis=analysis_result.get('core_analysis', ''),
            causal_chain=analysis_result.get('causal_chain', []),
            assumptions=analysis_result.get('assumptions', []),
            mental_model=analysis_result.get('mental_model', 'unknown'),
            counter_thesis=analysis_result.get('counter_thesis_scenarios', []),
            metrics_to_track=analysis_result.get('metrics_to_track', []),
            monitoring_plan=analysis_result.get('monitoring_plan', {})
        )
        
        db.session.add(thesis_analysis)
        db.session.flush()  # Get the ID
        
        # Create signal monitoring records
        for signal in signals_result.get('raw_signals', []):
            signal_monitor = SignalMonitoring(
                thesis_analysis_id=thesis_analysis.id,
                signal_name=signal.get('name', 'Unknown Signal'),
                signal_type=signal.get('level', 'unknown'),
                threshold_value=signal.get('threshold', 0),
                threshold_type=signal.get('threshold_type', 'change_percent'),
                status='active'
            )
            db.session.add(signal_monitor)
        
        db.session.commit()
        logging.info(f"Published thesis analysis: {thesis_analysis.title} (ID: {thesis_analysis.id})")
        return thesis_analysis.id
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error saving thesis analysis: {str(e)}")
        
        # Try to reconnect and retry once
        try:
            db.session.close()
            db.session.remove()
            
            # Retry the save operation
            thesis_analysis = ThesisAnalysis(
                title=analysis_result.get('core_claim', 'Untitled Thesis')[:255],
                original_thesis=thesis_text,
                core_claim=analysis_result.get('core_claim', ''),
                causal_chain=analysis_result.get('causal_chain', []),
                assumptions=analysis_result.get('assumptions', []),
                mental_model=analysis_result.get('mental_model', 'unknown'),
                counter_thesis=analysis_result.get('counter_thesis_scenarios', []),
                metrics_to_track=analysis_result.get('metrics_to_track', []),
                monitoring_plan=analysis_result.get('monitoring_plan', {})
            )
            
            db.session.add(thesis_analysis)
            db.session.flush()
            
            # Create signal monitoring records
            for signal in signals_result.get('raw_signals', []):
                signal_monitor = SignalMonitoring(
                    thesis_analysis_id=thesis_analysis.id,
                    signal_name=signal.get('name', 'Unknown Signal'),
                    signal_type=signal.get('level', 'unknown'),
                    threshold_value=signal.get('threshold', 0),
                    threshold_type=signal.get('threshold_type', 'change_percent'),
                    status='active'
                )
                db.session.add(signal_monitor)
            
            db.session.commit()
            logging.info(f"Successfully saved thesis analysis on retry: {thesis_analysis.title}")
            return thesis_analysis
            
        except Exception as retry_error:
            db.session.rollback()
            logging.error(f"Retry failed: {str(retry_error)}")
            raise

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
        
        # Analyze thesis using reliable service with intelligent fallbacks
        from services.reliable_analysis_service import ReliableAnalysisService
        reliable_service = ReliableAnalysisService()
        analysis_result = reliable_service.analyze_thesis(thesis_text)
        
        # Extract signals from AI analysis and documents using the classification hierarchy
        signals_result = signal_classifier.extract_signals_from_ai_analysis(
            analysis_result, 
            processed_documents, 
            focus_primary=focus_primary_signals
        )
        
        # Save analysis to database for monitoring
        thesis_id = save_thesis_analysis(thesis_text, analysis_result, signals_result)
        
        # Combine results
        combined_result = {
            'thesis_analysis': analysis_result,
            'signal_extraction': signals_result,
            'processed_documents': len(processed_documents),
            'focus_primary_signals': focus_primary_signals,
            'thesis_id': thesis_id,
            'published': True
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
    """Monitoring dashboard showing published thesis analyses and active signals"""
    try:
        # Get all published thesis analyses
        thesis_analyses = ThesisAnalysis.query.order_by(ThesisAnalysis.created_at.desc()).all()
        
        # Get active signals with thesis context
        active_signals = db.session.query(SignalMonitoring, ThesisAnalysis.title)\
            .join(ThesisAnalysis)\
            .filter(SignalMonitoring.status == 'active')\
            .order_by(SignalMonitoring.created_at.desc())\
            .all()
        
        # Get recent notifications
        recent_notifications = NotificationLog.query\
            .order_by(NotificationLog.sent_at.desc())\
            .limit(20).all()
        
        # Calculate monitoring statistics
        stats = {
            'total_published': len(thesis_analyses),
            'active_signals': len(active_signals),
            'triggered_signals': SignalMonitoring.query.filter_by(status='triggered').count(),
            'recent_notifications': len(recent_notifications)
        }
        
        return render_template('monitoring.html', 
                             thesis_analyses=thesis_analyses,
                             active_signals=active_signals,
                             recent_notifications=recent_notifications,
                             stats=stats)
    except Exception as e:
        return f"Error loading monitoring dashboard: {str(e)}", 500

@app.route('/thesis/<int:id>/monitor')
def monitor_thesis(id):
    """View monitoring status for a specific published thesis"""
    try:
        thesis = ThesisAnalysis.query.get_or_404(id)
        signals = SignalMonitoring.query.filter_by(thesis_analysis_id=id).all()
        
        # Debug logging
        print(f"Loading monitoring for thesis {id}")
        print(f"Found {len(signals)} signals")
        for signal in signals:
            print(f"Signal: {signal.signal_name}, Status: {signal.status}, Type: {signal.signal_type}")
        
        # Get notifications with better error handling
        notifications = []
        try:
            notifications = db.session.query(NotificationLog)\
                .join(SignalMonitoring)\
                .filter(SignalMonitoring.thesis_analysis_id == id)\
                .order_by(NotificationLog.sent_at.desc())\
                .all()
        except Exception as notif_error:
            print(f"Error loading notifications: {notif_error}")
            notifications = []
        
        print(f"Found {len(notifications)} notifications")
        
        return render_template('thesis_monitor.html',
                             thesis=thesis,
                             signals=signals,
                             notifications=notifications)
    except Exception as e:
        print(f"Error in monitor_thesis: {str(e)}")
        return f"Error loading thesis monitoring: {str(e)}", 500

@app.route('/api/thesis/<int:id>/status')
def get_thesis_status(id):
    """Get current monitoring status for a published thesis"""
    try:
        thesis = ThesisAnalysis.query.get_or_404(id)
        signals = SignalMonitoring.query.filter_by(thesis_analysis_id=id).all()
        
        signal_status = {
            'active': len([s for s in signals if s.status == 'active']),
            'triggered': len([s for s in signals if s.status == 'triggered']),
            'inactive': len([s for s in signals if s.status == 'inactive'])
        }
        
        return jsonify({
            'thesis_id': id,
            'title': thesis.title,
            'published_at': thesis.created_at.isoformat(),
            'signal_status': signal_status,
            'total_signals': len(signals),
            'last_checked': max([s.last_checked for s in signals if s.last_checked], default=None)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/signals/check', methods=['POST'])
def check_signals():
    """API endpoint to manually trigger signal checking"""
    try:
        results = signal_classifier.extract_signals_from_analysis("", [], focus_primary=True)
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

@app.route('/publish_thesis', methods=['POST'])
def publish_thesis():
    """Publish a completed thesis analysis for monitoring and simulation"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        # Extract thesis and signal data
        thesis_data = data.get('thesis_analysis', {})
        signal_data = data.get('signal_extraction', {})
        
        if not thesis_data.get('core_claim'):
            return jsonify({'success': False, 'error': 'Invalid thesis data'}), 400
        
        # Save thesis analysis
        thesis_id = save_thesis_analysis(
            thesis_data.get('original_thesis', 'Published thesis'), 
            thesis_data, 
            signal_data
        )
        
        return jsonify({
            'success': True, 
            'thesis_id': thesis_id,
            'message': 'Thesis published successfully'
        })
        
    except Exception as e:
        logging.error(f"Error publishing thesis: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/simulation/<int:thesis_id>')
def simulation_page(thesis_id):
    """Thesis simulation testing page"""
    try:
        thesis = ThesisAnalysis.query.get_or_404(thesis_id)
        return render_template('simulation.html', thesis=thesis)
    except Exception as e:
        logging.error(f"Error loading simulation page: {str(e)}")
        return render_template('404.html'), 404

@app.route('/api/simulation/run', methods=['POST'])
def run_simulation():
    """Run thesis simulation with time horizon forecasts and event scenarios"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No simulation data provided'}), 400
            
        simulation_type = data.get('simulation_type')
        thesis_id = data.get('thesis_id')
        
        if not simulation_type or not thesis_id:
            return jsonify({'error': 'Missing simulation type or thesis ID'}), 400
            
        # Get thesis data
        thesis = ThesisAnalysis.query.get_or_404(thesis_id)
        
        # Import simulation service
        from services.simulation_service import SimulationService
        simulation_service = SimulationService()
        
        if simulation_type == 'forecast':
            time_horizon = data.get('time_horizon')
            scenario_type = data.get('scenario_type')
            
            result = simulation_service.run_time_horizon_forecast(
                thesis, time_horizon, scenario_type
            )
            
        elif simulation_type == 'event':
            event_type = data.get('event_type')
            event_severity = data.get('event_severity')
            
            result = simulation_service.run_event_simulation(
                thesis, event_type, event_severity
            )
            
        else:
            return jsonify({'error': 'Invalid simulation type'}), 400
            
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error running simulation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
