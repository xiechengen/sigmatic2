import pandas as pd
import os
from werkzeug.utils import secure_filename
from flask import current_app
import json

class DataProcessor:
    def __init__(self):
        self.allowed_extensions = {'csv'}
    
    def allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def validate_csv(self, file_path):
        """Validate CSV file and return basic info"""
        try:
            df = pd.read_csv(file_path)
            return {
                'success': True,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'data_types': df.dtypes.to_dict(),
                'sample_data': df.head(5).to_dict('records')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def save_file_to_session(self, file, session_data):
        """Save uploaded file and store metadata in session"""
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Validate the CSV
            validation = self.validate_csv(file_path)
            
            if validation['success']:
                # Store file info in session
                if 'uploaded_files' not in session_data:
                    session_data['uploaded_files'] = []
                
                file_info = {
                    'filename': filename,
                    'file_path': file_path,
                    'rows': validation['rows'],
                    'columns': validation['columns'],
                    'column_names': validation['column_names'],
                    'data_types': {str(k): str(v) for k, v in validation['data_types'].items()},
                    'sample_data': validation['sample_data']
                }
                
                session_data['uploaded_files'].append(file_info)
                return {'success': True, 'file_info': file_info}
            else:
                # Remove invalid file
                os.remove(file_path)
                return {'success': False, 'error': validation['error']}
        
        return {'success': False, 'error': 'Invalid file type or no file provided'}
    
    def get_session_data_summary(self, session_data):
        """Get summary of uploaded files in session"""
        if 'uploaded_files' not in session_data:
            return []
        
        summary = []
        for file_info in session_data['uploaded_files']:
            summary.append({
                'filename': file_info['filename'],
                'rows': file_info['rows'],
                'columns': file_info['columns'],
                'column_names': file_info['column_names']
            })
        
        return summary
    
    def load_dataframe(self, filename, session_data):
        """Load a specific dataframe from session files"""
        if 'uploaded_files' not in session_data:
            return None
        
        for file_info in session_data['uploaded_files']:
            if file_info['filename'] == filename:
                try:
                    return pd.read_csv(file_info['file_path'])
                except Exception as e:
                    return None
        
        return None
    
    def cleanup_session_files(self, session_data):
        """Clean up uploaded files when session ends"""
        if 'uploaded_files' in session_data:
            for file_info in session_data['uploaded_files']:
                try:
                    if os.path.exists(file_info['file_path']):
                        os.remove(file_info['file_path'])
                except Exception:
                    pass
            session_data['uploaded_files'] = [] 