from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from app.utils.data_processor import DataProcessor
from app.utils.query_processor import QueryProcessor
from app.utils.visualization_processor import VisualizationProcessor
from datetime import datetime
import os

main = Blueprint('main', __name__)
data_processor = DataProcessor()
query_processor = QueryProcessor()
visualization_processor = VisualizationProcessor()

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

@main.route('/visualize', methods=['POST'])
def generate_visualization():
    """Generate visualization from natural language query"""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'success': False, 'error': 'No query provided'})
    
    query = data['query'].strip()
    chart_type = data.get('chart_type')  # Optional chart type override
    
    if not query:
        return jsonify({'success': False, 'error': 'Query cannot be empty'})
    
    # Check if data is uploaded
    if 'uploaded_files' not in session or not session['uploaded_files']:
        return jsonify({'success': False, 'error': 'No data uploaded. Please upload CSV files first.'})
    
    # Generate visualization
    result = visualization_processor.generate_chart(query, session, chart_type)
    
    return jsonify(result)

@main.route('/dashboard', methods=['GET'])
def get_dashboard():
    """Get current dashboard with pinned charts"""
    if 'dashboard_charts' not in session:
        session['dashboard_charts'] = []
    
    print(f"Dashboard requested. Total charts in session: {len(session['dashboard_charts'])}")
    print(f"Dashboard charts: {session['dashboard_charts']}")
    
    return jsonify({
        'success': True,
        'charts': session['dashboard_charts']
    })

@main.route('/dashboard/pin', methods=['POST'])
def pin_chart_to_dashboard():
    """Pin a chart to the dashboard"""
    data = request.get_json()
    
    if not data or 'chart' not in data:
        return jsonify({'success': False, 'error': 'No chart data provided'})
    
    if 'dashboard_charts' not in session:
        session['dashboard_charts'] = []
    
    # Add chart to dashboard
    chart_info = {
        'id': f"chart_{len(session['dashboard_charts']) + 1}",
        'title': data.get('title', 'Chart'),
        'chart': data['chart'],
        'timestamp': datetime.now().isoformat()
    }
    
    session['dashboard_charts'].append(chart_info)
    
    # Mark session as modified
    session.modified = True
    
    print(f"Pinned chart to dashboard. Total charts: {len(session['dashboard_charts'])}")
    print(f"Chart info: {chart_info}")
    
    return jsonify({
        'success': True,
        'message': 'Chart pinned to dashboard',
        'chart_id': chart_info['id']
    })

@main.route('/chart-image/<path:filename>')
def serve_chart_image(filename):
    """Serve chart images from the exports/charts directory"""
    from flask import send_from_directory
    import os
    # Use absolute path to the exports/charts directory
    chart_dir = os.path.join(os.getcwd(), 'exports', 'charts')
    print(f"Serving chart image: {filename}")
    print(f"Chart directory: {chart_dir}")
    print(f"Directory exists: {os.path.exists(chart_dir)}")
    if os.path.exists(chart_dir):
        print(f"Files in directory: {os.listdir(chart_dir)}")
    return send_from_directory(chart_dir, filename)

@main.route('/dashboard/remove/<chart_id>', methods=['DELETE'])
def remove_chart_from_dashboard(chart_id):
    """Remove a chart from the dashboard"""
    if 'dashboard_charts' not in session:
        return jsonify({'success': False, 'error': 'No dashboard charts found'})
    
    # Remove chart by ID
    session['dashboard_charts'] = [
        chart for chart in session['dashboard_charts']
        if chart['id'] != chart_id
    ]
    
    # Mark session as modified
    session.modified = True
    
    return jsonify({
        'success': True,
        'message': 'Chart removed from dashboard'
    })

@main.route('/test-session', methods=['GET'])
def test_session():
    """Test session functionality"""
    if 'test_counter' not in session:
        session['test_counter'] = 0
    
    session['test_counter'] += 1
    session.modified = True
    
    return jsonify({
        'success': True,
        'test_counter': session['test_counter'],
        'dashboard_charts_count': len(session.get('dashboard_charts', []))
    }) 