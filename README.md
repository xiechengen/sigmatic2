# Sigmatic - Natural Language Data Chatbox

A Flask-based web application that allows users to query data using natural language and instantly generate configurable reports and dashboards.

## Features

### Phase 1 (Current) - Foundation & Data Upload ✅
- **File Upload**: Support for up to 2 CSV files per session
- **Data Validation**: Automatic CSV validation and preview
- **Session Management**: Temporary storage with automatic cleanup
- **Responsive UI**: Modern, mobile-friendly interface

### Phase 2 (Coming Soon) - Natural Language Query Processing
- Natural language query interpretation using OpenAI API
- Text-based report generation
- Query-to-pandas transformation

### Phase 3 (Coming Soon) - Visualization & Dashboard
- Dynamic chart generation using Plotly
- Dashboard with pinned visualizations
- Interactive plot customization

### Phase 4 (Coming Soon) - Interactive Refinement
- Query refinement system
- Dynamic plot updates
- Filter and axis modification

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sigmatic
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   **Option A: Create a `.env` file**
   Create a `.env` file in the root directory:
   ```bash
   # OpenAI API Configuration
   OPENAI_API_KEY=your-openai-api-key-here
   
   # Flask Configuration
   SECRET_KEY=your-secret-key-here
   ```
   
   **Option B: Set environment variables directly**
   ```bash
   export OPENAI_API_KEY='your-openai-api-key-here'
   export SECRET_KEY='your-secret-key-here'
   ```
   
   **Get your OpenAI API key:**
   - Visit https://platform.openai.com/account/api-keys
   - Create a new API key
   - Copy the key and replace `your-openai-api-key-here` above

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Access the application**
   Open your browser and go to `http://localhost:5000`

## Usage

### Uploading Data
1. Click "Choose File" and select a CSV file
2. Click "Upload File" to process and validate the data
3. View file statistics (rows, columns) in the uploaded files list
4. Click "Preview" to see the first 10 rows of data

### Managing Files
- Upload up to 2 CSV files per session
- Remove individual files using the "Remove" button
- Clear all files using "Clear All Files"
- Files are automatically cleaned up when the session ends

### Data Preview
- View uploaded data in a responsive table format
- See column names and data types
- Preview first 10 rows of each dataset

## Project Structure

```
sigmatic/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── routes.py                # Main application routes
│   ├── utils/
│   │   ├── __init__.py
│   │   └── data_processor.py    # CSV processing utilities
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css        # Custom styles
│   │   ├── js/
│   │   │   └── app.js           # Frontend JavaScript
│   │   └── uploads/             # Temporary file storage
│   └── templates/
│       └── index.html           # Main application template
├── config.py                    # Application configuration
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
└── README.md                    # This file
```

## Technical Stack

- **Backend**: Flask 2.3.3
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5.3.0
- **Data Processing**: Pandas 2.1.1, NumPy 1.24.3
- **AI Integration**: OpenAI API (for Phase 2)
- **Visualization**: Plotly 5.17.0 (for Phase 3)
- **File Handling**: Werkzeug 2.3.7

## Development

### Running in Development Mode
```bash
python run.py
```

### Running with Gunicorn (Production)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## Security Features

- File type validation (CSV only)
- File size limits (16MB max)
- Session-based temporary storage
- Automatic file cleanup
- Input sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository.
