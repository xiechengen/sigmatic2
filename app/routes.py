from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from app.utils.data_processor import DataProcessor
from app.utils.query_processor import QueryProcessor
import os

main = Blueprint('main', __name__)
data_processor = DataProcessor()
query_processor = QueryProcessor()

@main.route('/')
def index():
    """Main application page"""
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    # Check if we already have 2 files uploaded
    if 'uploaded_files' in session and len(session['uploaded_files']) >= 2:
        return jsonify({'success': False, 'error': 'Maximum 2 files allowed'})
    
    # Process the file
    result = data_processor.save_file_to_session(file, session)
    
    if result['success']:
        session.modified = True
        return jsonify({
            'success': True,
            'message': f'File {file.filename} uploaded successfully',
            'file_info': result['file_info']
        })
    else:
        return jsonify({'success': False, 'error': result['error']})

@main.route('/files')
def get_files():
    """Get list of uploaded files"""
    summary = data_processor.get_session_data_summary(session)
    return jsonify({'files': summary})

@main.route('/preview/<filename>')
def preview_file(filename):
    """Preview a specific file's data"""
    df = data_processor.load_dataframe(filename, session)
    if df is not None:
        return jsonify({
            'success': True,
            'data': df.head(10).to_dict('records'),
            'columns': df.columns.tolist()
        })
    else:
        return jsonify({'success': False, 'error': 'File not found'})

@main.route('/clear-session', methods=['POST'])
def clear_session():
    """Clear all uploaded files and session data"""
    data_processor.cleanup_session_files(session)
    session.clear()
    return jsonify({'success': True, 'message': 'Session cleared'})

@main.route('/remove-file/<filename>', methods=['POST'])
def remove_file(filename):
    """Remove a specific file from session"""
    if 'uploaded_files' in session:
        for i, file_info in enumerate(session['uploaded_files']):
            if file_info['filename'] == filename:
                # Remove file from disk
                try:
                    if os.path.exists(file_info['file_path']):
                        os.remove(file_info['file_path'])
                except Exception:
                    pass
                
                # Remove from session
                session['uploaded_files'].pop(i)
                session.modified = True
                return jsonify({'success': True, 'message': f'File {filename} removed'})
    
    return jsonify({'success': False, 'error': 'File not found'})

@main.route('/query', methods=['POST'])
def process_query():
    """Process natural language query"""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'success': False, 'error': 'No query provided'})
    
    query = data['query'].strip()
    
    if not query:
        return jsonify({'success': False, 'error': 'Query cannot be empty'})
    
    # Process the query
    result = query_processor.process_query(query, session)
    
    return jsonify(result) 