import json
from typing import Dict, Any, List
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
from .topic_manager import TopicManager
import asyncio
import pandas as pd

class ChartAgent:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Configure OpenAI API
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in .env file")
            
        # Initialize AsyncOpenAI client with minimal configuration
        self.client = AsyncOpenAI(
            api_key=api_key
        )
        
        self.topic_manager = TopicManager()
        self.current_data = None
        self.current_config = None
        
    async def process_command(self, data: Any, command: str) -> Dict:
        """
        Process a command and generate chart configuration
        """
        # Check if this is a new topic
        if self.topic_manager.is_new_topic(command):
            self.current_config = None
        
        # Store current data
        self.current_data = data
        
        # Prepare the context for the AI
        context = self._prepare_context(data, command)
        
        print(context)
        
        # Generate chart configuration using AI
        response = await self._generate_config(context)
        chart_config = response.get("chart_config")
        candidate_questions = response.get("candidate_questions", [])
        
        print("complete the processing command")
        print(chart_config)
        
        # Store the current configuration
        if chart_config:
            self.current_config = chart_config
        
        return {
            "chart_config": chart_config,
            "candidate_questions": candidate_questions
        }
    
    async def update_chart(self, command: str) -> Dict:
        """Update existing chart based on new command"""
        try:
            if self.current_config is None:
                raise ValueError("No existing chart to update")
            
            if self.current_data is None:
                raise ValueError("No data available for update")
            
            # Convert DataFrame to dict only if it's a DataFrame
            data_dict = self.current_data.to_dict('records') if hasattr(self.current_data, 'to_dict') else self.current_data
            
            context = {
                "data": data_dict,
                "command": command,
                "current_config": self.current_config
            }
            
            # Generate updated configuration using AI
            response = await self._generate_config(context)
            
            # Check if response is a dict with chart_config and candidate_questions
            if isinstance(response, dict):
                chart_config = response.get("chart_config")
                candidate_questions = response.get("candidate_questions", [])
                
                # Update current config if we got a new one
                if chart_config:
                    self.current_config = chart_config
                    
                return {
                    "chart_config": chart_config,
                    "candidate_questions": candidate_questions
                }
            else:
                # Handle legacy format (just the config)
                self.current_config = response
                return {
                    "chart_config": response,
                    "candidate_questions": []
                }
        
        except Exception as e:
            raise ValueError(f"Error updating chart: {str(e)}")
    
    def _prepare_context(self, data: Any, command: str) -> Dict:
        """Prepare context for AI processing"""
        # Convert DataFrame to dict only if it's a DataFrame
        data_dict = data.to_dict('records') if hasattr(data, 'to_dict') else data
        
        return {
            "data": data_dict,
            "command": command,
            "current_config": self.current_config
        }
    
    async def _generate_config(self, context: Dict) -> Dict:
        """Generate chart configuration using AI"""
        try:
            system_message = """You are a Chart.js configuration expert and a data analysis assistant. Your role is to:
1. Analyze both the input data structure and the semantic context of the data.
2. Classify data types (numerical, categorical, temporal) and understand their real-world meaning.
3. Transform data precisely according to user requests, ensuring transformations align with both data types and contextual meaning.
4. Generate valid Chart.js configurations based on the analysis of the data and the user's prompt.
5. Please make sure that the chart_config is not None and has correct syntax.
6. Always generate 3-5 candidate questions to clarify the user's intent. These questions should help narrow down the user's requirements and ensure accurate chart generation.
7. Follow this exact JSON structure to include Chart.js configuration and clarification questions:
    {
        "chart_config": {
            "type": "bar|line|pie|doughnut|radar|polarArea|bubble|scatter",
            "data": {
                "labels": ["label1", "label2", ...],
                "datasets": [
                    {
                        "label": "Dataset Label",
                        "data": [value1, value2, ...],
                        "backgroundColor": ["color1", "color2", ...],
                        "borderColor": ["color1", "color2", ...],
                        // other dataset properties as needed
                    }
                ]
            },
            "options": {
                "scales": {
                    "x": {
                        "title": {
                            "display": true,
                            "text": "X-Axis Label"
                        }
                    },
                    "y": {
                        "title": {
                            "display": true,
                            "text": "Y-Axis Label"
                        }
                    }
                },
                "plugins": {
                    "title": {
                        "display": true,
                        "text": "Chart Title"
                    },
                    "legend": {
                        "position": "top"
                    }
                },
                // other chart options as needed
            }
        },
        "candidate_questions": [
            "Question 1?",
            "Question 2?",
            "Question 3?"
        ]
    }

8. Ensure all JSON keys and values use double quotes, not single quotes.
9. For color values, use standard CSS color names, hex codes, or rgba() format.
10. Include proper axis formatting with titles and scales appropriate to the data.
11. Set sensible defaults for colors, labels, and other visual elements.
12. For time-series data, use the appropriate time scale configuration.
"""

            user_prompt = self._create_prompt(context)
            
            try:
                async with asyncio.timeout(60):  # Increase timeout to 60 seconds
                    response = await self.client.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.3,  # Lower temperature for more precise output
                        max_tokens=2000,
                        response_format={"type": "json_object"}  # Force JSON output
                    )
            except asyncio.TimeoutError:
                # Handle timeout specifically
                return {
                    "chart_config": None,
                    "candidate_questions": ["Could you simplify your request? The previous one timed out."]
                }
            
            content = response.choices[0].message.content
            print("Raw AI response:", content)
            
            try:
                # Try to parse as JSON
                parsed_content = json.loads(content)
                
                # Check if it has the expected structure
                if "chart_config" in parsed_content:
                    return parsed_content
                elif "candidate_questions" in parsed_content:
                    return {
                        "chart_config": None,
                        "candidate_questions": parsed_content["candidate_questions"]
                    }
                else:
                    # If it's valid JSON but missing expected keys, wrap it as chart_config
                    return {
                        "chart_config": parsed_content,
                        "candidate_questions": []
                    }
            except json.JSONDecodeError:
                # If JSON parsing fails, extract candidate questions from text
                candidate_questions = self._extract_candidate_questions(content)
                if candidate_questions:
                    return {
                        "chart_config": None,
                        "candidate_questions": candidate_questions
                    }
                else:
                    # If we can't extract questions, return a fallback error
                    return {
                        "chart_config": None,
                        "candidate_questions": ["I couldn't understand the data. Could you try a simpler request?"]
                    }
            
        except Exception as e:
            print(f"Error in _generate_config: {str(e)}")
            # Return a graceful error response instead of raising an exception
            return {
                "chart_config": None,
                "candidate_questions": [
                    f"An error occurred: {str(e)}. Could you try a different request?",
                    "Is your data in the correct format?",
                    "Try simplifying your request."
                ]
            }
    
    def _create_prompt(self, context: Dict) -> str:
        """Create a precise prompt for the AI"""
        return f"""DATA STRUCTURE:
{json.dumps(self._analyze_data_structure(context['data']), indent=2)}

ORIGINAL DATA:
{json.dumps(context['data'], indent=2)}

COMMAND: {context['command']}

PREVIOUS CONFIG: {json.dumps(context['current_config'], indent=2) if context['current_config'] else 'null'}

REQUIREMENTS:
1. Generate a complete Chart.js configuration
2. Include all necessary data transformations
3. Follow this exact structure:
{{
    "type": "<chart_type>",
    "data": {{
        "labels": [],
        "datasets": [
            {{
                "label": "<dataset_label>",
                "data": [],
                ... other dataset options
            }}
        ]
    }},
    "options": {{
        ... required chart options
    }}
}}

4. For time-based data:
   - Handle date formatting
   - Support aggregations (daily→weekly→monthly→quarterly)
   - Calculate growth rates when requested
   - Include moving averages if needed

5. For numerical data:
   - Calculate proper scales
   - Handle aggregations
   - Support multiple axes if needed
   - Format numbers appropriately

6. For categorical data:
   - Group data correctly
   - Calculate proportions if needed
   - Sort data when appropriate
   - Handle multiple categories

Generate the Chart.js configuration now, and if the prompt is unclear, provide 3-5 candidate questions for clarification:"""

    def _analyze_data_structure(self, data: Any) -> Dict:
        """Analyze data structure with enhanced detail"""
        # If data is already a dict (from previous conversion), convert it back to DataFrame
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            try:
                data = pd.DataFrame(data)
            except (ValueError, TypeError) as e:
                print(f"Warning: Failed to convert data to DataFrame: {str(e)}")
                pass
            
        analysis = {
            "columns": {},
            "temporal_patterns": [],
            "numerical_columns": [],
            "categorical_columns": [],
            "statistics": {},
            "relationships": []
        }

        try:
            # Handle pandas DataFrame
            if hasattr(data, 'dtypes') and not data.empty:
                # Enhanced DataFrame analysis
                for col in data.columns:
                    dtype = str(data[col].dtype)
                    
                    # Safe statistics calculation
                    stats = {
                        "unique_count": int(data[col].nunique()),
                        "missing_count": int(data[col].isna().sum()),
                        "sample_values": data[col].dropna().head(3).tolist()
                    }
                    
                    # Add numerical statistics if applicable
                    if dtype in ['int64', 'float64']:
                        numeric_data = data[col].dropna()
                        if not numeric_data.empty:
                            stats.update({
                                "min": float(numeric_data.min()),
                                "max": float(numeric_data.max()),
                                "mean": float(numeric_data.mean())
                            })
                    
                    analysis["columns"][col] = {
                        "type": dtype,
                        "stats": stats
                    }

                    # Enhanced temporal pattern detection
                    if dtype.startswith('datetime'):
                        date_data = data[col].dropna()
                        if not date_data.empty:
                            freq = pd.infer_freq(date_data)
                            if freq:
                                analysis["temporal_patterns"].append({
                                    "column": col,
                                    "frequency": freq,
                                    "range": {
                                        "start": date_data.min().strftime('%Y-%m-%d'),
                                        "end": date_data.max().strftime('%Y-%m-%d')
                                    }
                                })

                    # Categorize columns with more detail
                    if dtype in ['int64', 'float64']:
                        numeric_data = data[col].dropna()
                        if not numeric_data.empty:
                            analysis["numerical_columns"].append({
                                "name": col,
                                "range": [float(numeric_data.min()), float(numeric_data.max())],
                                "distribution": "continuous"
                            })
                    else:
                        unique_vals = data[col].dropna().unique()
                        analysis["categorical_columns"].append({
                            "name": col,
                            "unique_values": list(unique_vals)[:5],
                            "is_ordered": bool(data[col].dtype.name == 'category' and data[col].dtype.ordered)
                        })

                # Add basic correlation analysis for numerical columns
                numerical_cols = [col["name"] for col in analysis["numerical_columns"]]
                if len(numerical_cols) > 1:
                    numeric_data = data[numerical_cols].dropna()
                    if not numeric_data.empty:
                        corr_matrix = numeric_data.corr()
                        analysis["relationships"] = [
                            {
                                "columns": [col1, col2],
                                "correlation": float(corr_matrix.loc[col1, col2])
                            }
                            for col1 in corr_matrix.columns
                            for col2 in corr_matrix.columns
                            if col1 < col2 and abs(corr_matrix.loc[col1, col2]) > 0.5
                        ]
            # Handle dictionary data
            elif isinstance(data, dict):
                analysis["data_type"] = "dictionary"
                analysis["structure"] = {
                    "keys": list(data.keys()),
                    "sample_values": {k: type(v).__name__ for k, v in data.items()}
                }

        except (ValueError, TypeError, AttributeError, pd.errors.EmptyDataError) as e:
            print(f"Warning: Error analyzing data structure: {str(e)}")
            analysis["error"] = str(e)

        return analysis 

    def _extract_candidate_questions(self, content: str) -> List[str]:
        """Extract candidate questions from the AI response"""
        try:
            # First try to parse as JSON
            data = json.loads(content)
            if isinstance(data, dict) and "candidate_questions" in data:
                return data["candidate_questions"]
        except json.JSONDecodeError:
            pass
        
        # If JSON parsing fails, try to extract from text
        questions = []
        lines = content.splitlines()
        
        # Look for sections that might contain questions
        in_questions_section = False
        for line in lines:
            line = line.strip()
            
            # Check if we're entering a questions section
            if "candidate questions" in line.lower() or "follow-up questions" in line.lower():
                in_questions_section = True
                continue
            
            # If we're in a questions section, extract questions
            if in_questions_section:
                # Skip empty lines or section headers
                if not line or line.endswith(':'):
                    continue
                    
                # Check for common question formats
                if line.startswith('-') or line.startswith('*'):
                    questions.append(line[1:].strip())
                elif line.startswith('1.') or line.startswith('2.') or line.startswith('3.'):
                    # Extract numbered questions
                    questions.append(line[line.find('.')+1:].strip())
                elif '?' in line:
                    # If it contains a question mark, it's probably a question
                    questions.append(line)
        
        return questions 