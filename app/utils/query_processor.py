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

IMPORTANT: The dataframes are already loaded in memory. DO NOT use pd.read_csv() or any file reading functions.

Available datasets (already loaded as dataframes):
{data_context}

Query: "{query}"

WARNING: Only use columns that are listed in the "Available columns" section above. Do NOT assume columns like WEIGHT, HEIGHT, etc. exist unless they are listed.

Generate pandas code that:
1. Uses the dataframes that are already loaded (do NOT read files)
2. Performs the requested analysis using ONLY available columns
3. Stores the result in a variable called 'result'
4. Handles missing values appropriately using .dropna() or .fillna()
5. Uses descriptive variable names
6. Handles data type conversions properly (use .astype() when needed)
7. Avoids string concatenation with mixed types
8. If the query mentions columns that don't exist, use similar available columns or explain the limitation
9. Handles data quality issues (missing values, placeholder values like "******")
10. For date operations, use .dropna() to remove invalid dates before processing

Available dataframe variables:
{', '.join([filename.replace('.csv', '').replace('-', '_').replace(' ', '_') for filename in dataframes.keys()])}

Available columns (after preprocessing):
{', '.join([f"{filename.replace('.csv', '').replace('-', '_').replace(' ', '_')}: {list(df.columns)}" for filename, df in dataframes.items()])}

Dataframe descriptions:
{', '.join([f"{filename.replace('.csv', '').replace('-', '_').replace(' ', '_')}: {filename} (demographics data)" if 'dm' in filename.lower() else f"{filename.replace('.csv', '').replace('-', '_').replace(' ', '_')}: {filename} (lab results)" if 'lb' in filename.lower() else f"{filename.replace('.csv', '').replace('-', '_').replace(' ', '_')}: {filename} (other data)" for filename in dataframes.keys()])}

Example: If you need to work with 'dm.csv', use the variable 'dm' (not pd.read_csv('dm.csv'))

IMPORTANT EXAMPLES:
- For patient demographics (age, sex, etc.): use 'dm' dataframe
- For lab results: use 'lb' dataframe  
- To select age column: result = dm[['AGE']]
- To filter by age: result = dm[dm['AGE'] > 70]
- To count patients: result = len(dm)
- To combine information: result = dm[['USUBJID', 'AGE', 'SEX']]
- NEVER do: dm[['AGE']] = ['AGE'] (this is wrong!)
- ONLY use columns that exist in the data (check the column list above)
- For age-related queries, ALWAYS use the 'dm' dataframe, not 'lb'

Common patterns:
- For counting: result = len(df) or result = df.shape[0]
- For filtering: result = df[df['column'] > value]
- For grouping: result = df.groupby('column').size() or result = df.groupby('column').count()
- For string operations: use .str methods, not + operator
- For type conversion: df['column'] = df['column'].astype(str) or df['column'] = pd.to_numeric(df['column'], errors='coerce')
- For selecting columns: use df[['col1', 'col2']] (list of column names)
- For combining data: use pd.concat() or merge(), not + operator
- For creating new columns: df['new_col'] = df['col1'].astype(str) + ' ' + df['col2'].astype(str)
- For date operations: df['date_col'] = pd.to_datetime(df['date_col'], errors='coerce'); df = df.dropna(subset=['date_col'])
- For date filtering: df[df['date_col'] > '1950-01-01'] (compare with string dates) or df[df['date_col'] > pd.to_datetime('1950-01-01')] (compare with datetime)
- NEVER use: df[['col1', 'col2']] = ['col1', 'col2'] (this creates a list, not a selection)

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
        
        # Add dataframes as individual variables with preprocessing
        for filename, df in dataframes.items():
            var_name = filename.replace('.csv', '').replace('-', '_').replace(' ', '_')
            
            # Clean column names (remove spaces, special characters)
            df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace('-', '_')
            
            # Ensure string columns are properly typed
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Handle placeholder values like "******" for missing dates
                    if df[col].str.contains('\*+', na=False).any():
                        # Replace asterisk placeholders with NaN for date columns
                        df[col] = df[col].replace(r'\*+', pd.NaT, regex=True)
                    
                    # Try to convert to numeric if possible, otherwise keep as string
                    try:
                        pd.to_numeric(df[col], errors='raise')
                        # If successful, convert to numeric
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    except (ValueError, TypeError):
                        # Try to convert to datetime if it looks like a date column
                        if any(date_keyword in col.upper() for date_keyword in ['DATE', 'DTC', 'DT']):
                            try:
                                df[col] = pd.to_datetime(df[col], errors='coerce')
                            except (ValueError, TypeError):
                                # Keep as string if datetime conversion fails
                                df[col] = df[col].astype(str)
                        else:
                            # Keep as string, ensure it's string type
                            df[col] = df[col].astype(str)
            
            local_vars[var_name] = df
        
        try:
            # Execute the code with minimal but necessary builtins
            safe_builtins = {
                '__import__': __import__,
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'sum': sum,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round,
                'sorted': sorted,
                'reversed': reversed,
                'any': any,
                'all': all,
                'isinstance': isinstance,
                'type': type,
                'hasattr': hasattr,
                'getattr': getattr,
                'setattr': setattr,
                'delattr': delattr,
                'dir': dir,
                'vars': vars,
                'locals': locals,
                'globals': globals,
                'id': id,
                'hash': hash,
                'repr': repr,
                'ascii': ascii,
                'bin': bin,
                'oct': oct,
                'hex': hex,
                'ord': ord,
                'chr': chr,
                'divmod': divmod,
                'pow': pow,
                'complex': complex,
                'bytes': bytes,
                'bytearray': bytearray,
                'memoryview': memoryview,
                'slice': slice,
                'property': property,
                'super': super,
                'object': object,
                'Exception': Exception,
                'BaseException': BaseException,
                'StopIteration': StopIteration,
                'GeneratorExit': GeneratorExit,
                'ArithmeticError': ArithmeticError,
                'BufferError': BufferError,
                'LookupError': LookupError,
                'AssertionError': AssertionError,
                'AttributeError': AttributeError,
                'EOFError': EOFError,
                'FloatingPointError': FloatingPointError,
                'ImportError': ImportError,
                'ModuleNotFoundError': ModuleNotFoundError,
                'IndexError': IndexError,
                'KeyError': KeyError,
                'KeyboardInterrupt': KeyboardInterrupt,
                'MemoryError': MemoryError,
                'NameError': NameError,
                'NotImplementedError': NotImplementedError,
                'OSError': OSError,
                'OverflowError': OverflowError,
                'RecursionError': RecursionError,
                'ReferenceError': ReferenceError,
                'RuntimeError': RuntimeError,
                'SyntaxError': SyntaxError,
                'SystemError': SystemError,
                'TypeError': TypeError,
                'UnboundLocalError': UnboundLocalError,
                'UnicodeError': UnicodeError,
                'ValueError': ValueError,
                'ZeroDivisionError': ZeroDivisionError,
                'BlockingIOError': BlockingIOError,
                'BrokenPipeError': BrokenPipeError,
                'ChildProcessError': ChildProcessError,
                'ConnectionError': ConnectionError,
                'FileExistsError': FileExistsError,
                'FileNotFoundError': FileNotFoundError,
                'InterruptedError': InterruptedError,
                'IsADirectoryError': IsADirectoryError,
                'NotADirectoryError': NotADirectoryError,
                'PermissionError': PermissionError,
                'ProcessLookupError': ProcessLookupError,
                'TimeoutError': TimeoutError,
                'open': open,
                'input': input,
                'help': help,
                'copyright': copyright,
                'credits': credits,
                'license': license,
                'exit': exit,
                'quit': quit
            }
            exec(code, {'__builtins__': safe_builtins}, local_vars)
            
            # Extract results
            result = local_vars.get('result')
            results = local_vars.get('results', {})
            
            # Convert results to serializable format
            if isinstance(result, pd.DataFrame):
                # Convert datetime objects to strings for JSON serialization
                df_copy = result.head(20).copy()
                for col in df_copy.columns:
                    if df_copy[col].dtype == 'datetime64[ns]':
                        df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d')
                    elif df_copy[col].dtype == 'object':
                        # Handle any remaining datetime objects in object columns
                        df_copy[col] = df_copy[col].astype(str)
                
                return {
                    'type': 'dataframe',
                    'data': df_copy.to_dict('records'),
                    'columns': result.columns.tolist(),
                    'total_rows': len(result),
                    'shape': result.shape
                }
            elif isinstance(result, pd.Series):
                # Convert datetime objects to strings for JSON serialization
                series_copy = result.copy()
                if series_copy.dtype == 'datetime64[ns]':
                    series_copy = series_copy.dt.strftime('%Y-%m-%d')
                elif series_copy.dtype == 'object':
                    # Handle any remaining datetime objects in object series
                    series_copy = series_copy.astype(str)
                
                return {
                    'type': 'series',
                    'data': series_copy.to_dict(),
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
            error_msg = str(e)
            
            # Provide more helpful error messages for common issues
            if "can only concatenate str (not" in error_msg:
                error_msg = f"Data type error: {error_msg}. This usually happens when trying to concatenate strings with numbers. Please check your query and ensure proper data type handling."
            elif "KeyError" in error_msg:
                error_msg = f"Column not found: {error_msg}. Please check the column names in your data."
            elif "NameError" in error_msg:
                error_msg = f"Variable not found: {error_msg}. Please check the dataframe variable names."
            elif "['WEIGHT']" in error_msg or "['AGE']" in error_msg:
                error_msg = f"Column selection error: {error_msg}. This happens when trying to use a list as a column name. Use df[['col1', 'col2']] to select multiple columns, not df[['col1']] = ['col1']."
            elif "list" in error_msg and "str" in error_msg:
                error_msg = f"List/string confusion: {error_msg}. Make sure you're using proper pandas syntax for column selection and operations."
            elif "Can only use .str accessor with string values" in error_msg:
                error_msg = f"String method error: {error_msg}. This happens when trying to use .str methods on datetime or numeric columns. Convert to string first with .astype(str) if needed."
            elif "'AGE'" in error_msg:
                error_msg = f"Column not found: {error_msg}. The AGE column is in the 'dm' (demographics) dataframe, not 'lb' (lab results). Use 'dm' for age-related queries."
            
            # Log the generated code for debugging
            print(f"Generated code that failed:")
            print(code)
            print(f"Error: {error_msg}")
            
            raise Exception(f"Error executing pandas code: {error_msg}\n\nGenerated code:\n{code}\n\nOriginal OpenAI response:\n{code}")
    
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
    
     