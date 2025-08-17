import pandas as pd
import openai
import json
import re
from typing import Dict, List, Any, Optional
from flask import current_app

class QueryProcessor:
    def __init__(self):
        self.openai_api_key = None
    
    def _get_openai_key(self):
        """Get OpenAI API key from current app context"""
        if not self.openai_api_key:
            try:
                self.openai_api_key = current_app.config.get('OPENAI_API_KEY')
                if self.openai_api_key:
                    openai.api_key = self.openai_api_key
            except RuntimeError:
                # Working outside of application context
                pass
        return self.openai_api_key
    
    def process_query(self, query: str, session_data: Dict) -> Dict[str, Any]:
        """
        Process a natural language query and return results
        """
        # Load dataframes from session
        dataframes = self._load_session_dataframes(session_data)
        if not dataframes:
            return {
                'success': False,
                'error': 'No data uploaded. Please upload CSV files first.'
            }
        
                # Check if OpenAI is available
        if not self._get_openai_key():
            return {
                'success': False,
                'error': 'OpenAI API key not configured. Please set OPENAI_API_KEY in your environment.'
            }

        try:
            # Generate pandas code from natural language query
            pandas_code = self._generate_pandas_code(query, dataframes)
            if not pandas_code:
                return {
                    'success': False,
                    'error': 'Could not interpret query. Please try rephrasing.'
                }
            
            # Execute the pandas code
            result = self._execute_pandas_code(pandas_code, dataframes)
            
            # Generate natural language report
            report = self._generate_report(query, result, pandas_code)
            
            return {
                'success': True,
                'result': result,
                'report': report,
                'pandas_code': pandas_code
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing query: {str(e)}'
            }
    
    def _load_session_dataframes(self, session_data: Dict) -> Dict[str, pd.DataFrame]:
        """Load all dataframes from session data"""
        dataframes = {}
        
        if 'uploaded_files' in session_data:
            for file_info in session_data['uploaded_files']:
                try:
                    df = pd.read_csv(file_info['file_path'])
                    # Clean column names (remove spaces, special chars)
                    df.columns = [col.strip().replace(' ', '_').replace('-', '_') for col in df.columns]
                    dataframes[file_info['filename']] = df
                except Exception as e:
                    print(f"Error loading {file_info['filename']}: {e}")
        
        return dataframes
    
    def _generate_pandas_code(self, query: str, dataframes: Dict[str, pd.DataFrame]) -> str:
        """Use OpenAI to generate pandas code from natural language query"""
        
        # Create context about available data
        data_context = self._create_data_context(dataframes)
        
        prompt = f"""
You are a data analyst working with clinical trial data. Convert the following natural language query into pandas code.

Available datasets:
{data_context}

Query: "{query}"

Generate pandas code that:
1. Uses the appropriate dataset(s)
2. Performs the requested analysis
3. Returns results in a clear format
4. Handles missing values appropriately
5. Uses descriptive variable names

Return ONLY the pandas code, no explanations. The code should be ready to execute.
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a data analyst expert in pandas and clinical trial data analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            code = response.choices[0].message.content.strip()
            
            # Clean up the code (remove markdown formatting if present)
            code = re.sub(r'```python\s*', '', code)
            code = re.sub(r'```\s*', '', code)
            
            return code
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None
    
    def _create_data_context(self, dataframes: Dict[str, pd.DataFrame]) -> str:
        """Create context description of available datasets"""
        context = []
        
        for filename, df in dataframes.items():
            context.append(f"\n{filename}:")
            context.append(f"  - Rows: {len(df)}")
            context.append(f"  - Columns: {len(df.columns)}")
            context.append(f"  - Column names: {list(df.columns)}")
            
            # Add sample data types for key columns
            sample_dtypes = df.dtypes.head(10).to_dict()
            context.append(f"  - Sample data types: {sample_dtypes}")
            
            # Add sample values for key columns
            if len(df) > 0:
                sample_values = {}
                for col in df.columns[:5]:  # First 5 columns
                    if df[col].dtype in ['object', 'string']:
                        unique_vals = df[col].dropna().unique()[:3]
                        sample_values[col] = list(unique_vals)
                    else:
                        sample_values[col] = f"numeric (min: {df[col].min()}, max: {df[col].max()})"
                context.append(f"  - Sample values: {sample_values}")
        
        return "\n".join(context)
    
    def _execute_pandas_code(self, code: str, dataframes: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Execute pandas code safely and return results"""
        
        # Create a safe execution environment
        local_vars = {
            'pd': pd,
            'dataframes': dataframes,
            'result': None,
            'results': {}
        }
        
        # Add dataframes as individual variables
        for filename, df in dataframes.items():
            var_name = filename.replace('.csv', '').replace('-', '_').replace(' ', '_')
            local_vars[var_name] = df
        
        try:
            # Execute the code
            exec(code, {'__builtins__': {}}, local_vars)
            
            # Extract results
            result = local_vars.get('result')
            results = local_vars.get('results', {})
            
            # Convert results to serializable format
            if isinstance(result, pd.DataFrame):
                return {
                    'type': 'dataframe',
                    'data': result.head(20).to_dict('records'),
                    'columns': result.columns.tolist(),
                    'total_rows': len(result),
                    'shape': result.shape
                }
            elif isinstance(result, pd.Series):
                return {
                    'type': 'series',
                    'data': result.to_dict(),
                    'index': result.index.tolist(),
                    'dtype': str(result.dtype)
                }
            elif isinstance(result, (int, float, str, bool)):
                return {
                    'type': 'scalar',
                    'value': result
                }
            elif isinstance(result, dict):
                return {
                    'type': 'dict',
                    'data': {k: str(v) if isinstance(v, (pd.DataFrame, pd.Series)) else v 
                            for k, v in result.items()}
                }
            else:
                return {
                    'type': 'other',
                    'data': str(result),
                    'results': results
                }
                
        except Exception as e:
            raise Exception(f"Error executing pandas code: {str(e)}")
    
    def _generate_report(self, query: str, result: Dict, pandas_code: str) -> str:
        """Generate natural language report from query results"""
        
        prompt = f"""
Generate a clear, concise report based on the following:

Query: "{query}"
Results: {json.dumps(result, indent=2)}

Write a natural language report that:
1. Summarizes the findings in plain English
2. Includes relevant statistics and numbers
3. Is easy to understand for non-technical users
4. Highlights key insights
5. Uses appropriate medical/clinical terminology if relevant

Keep the report under 200 words and focus on actionable insights.
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a medical data analyst writing clear reports for clinical trial data."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Analysis completed. Found {result.get('total_rows', 'unknown number of')} results." 
    
     