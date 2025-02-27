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
        candidate_questions = response.get("candidate_questions")
        
        print("complete the processing command")
        print(chart_config)
        print(candidate_questions)
        self.current_config = chart_config
        return chart_config
    
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
            
            updated_config = await self._generate_config(context)
            self.current_config = updated_config
            return updated_config
        
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
5. Everytime generate 3-5 candidate questions to clarify the user's intent. These questions should help narrow down the user's requirements and ensure accurate chart generation.
6. Follow json structure to include exact Chart.js syntax and structure and extra questions to clarify the user's intent: 
    for example:
        {
            "chart_config": {
                "type": "bar",
                "data": {
                    "labels": [],
                    "datasets": []
                },
                "options": {
                }
            },
            "candidate_questions": ["question1", "question2", "question3"]
        }

ALWAYS:
- Output only the Chart.js configuration JSON.
- Use double quotes for JSON strings.
- Include complete data transformations in the datasets.
- Follow Chart.js v3+ syntax.
- Provide insights based on the data analysis to inform the chart configuration.
- Handle special cases based on data context, not just data type.
- Filter out irrelevant data categories that don't match the user's intent.
- Understand the semantic meaning of data categories and filter accordingly.
- Consider the real-world meaning of data values when processing user requests.
- Choose appropriate chart types based on data characteristics and user intent.
- Set sensible defaults for colors, labels, and other visual elements.
- Include proper axis formatting and scales.

SPECIAL CASES:
- For categorical data: Distinguish between active/current vs. inactive/historical/special statuses.
- When user requests focus on specific category types, exclude unrelated categories even if they share similar naming.
- For financial data: Distinguish between different financial metrics appropriately.
- For temporal data: Handle different time granularities appropriately.
- For status-based data: Understand the difference between various status types and their relationships.
- For comparison requests: Highlight differences using appropriate visual techniques.
- For trend analysis: Use line charts with proper time-based x-axis configuration.
- For part-to-whole relationships: Use pie or doughnut charts with percentage calculations.
- For distribution data: Consider histograms or box plots with appropriate binning.

CHART TYPE SELECTION:
- Bar charts: For comparing quantities across categories
- Line charts: For showing trends over time or continuous variables
- Pie/Doughnut charts: For showing composition or part-to-whole relationships
- Scatter plots: For showing correlation between two variables
- Radar charts: For comparing multiple variables in a radial layout
- Bubble charts: For showing relationships between three variables
- Polar area charts: For showing cyclical or proportional data in a radial layout

NEVER:
- Include irrelevant categories that don't match the semantic intent of the user's request.
- Include explanations or markdown.
- Use single quotes.
- Skip required Chart.js options.
- Output incomplete JSON.
- Ignore the context of the user's prompt or the characteristics of the input data.
- Choose inappropriate chart types for the data structure or user intent.

Example:

    Input:
        subscription_tier,count
        ULTIMATE_MONTHLY,1
        CANCELLED_ULTIMATE_MONTHLY,2
        ULTIMATE_LIFETIME,1
        PRO_YEARLY,5
        CANCELLED_PLUS_YEARLY,5
        CANCELLED_PRO_YEARLY,2
        PRO_MONTHLY,8
        ULTIMATE_YEARLY,2
        FREE,4353
        INTENDED,73
        PLUS_MONTHLY,7
        PLUS_YEARLY,5
        CANCELLED_PLUS_MONTHLY,17
        CANCELLED_PRO_MONTHLY,20
    User prompt: Show me the number of active subscriptions by tier.
    
    In this case, please don't include the FREE category in the chart.
"""

            user_prompt = self._create_prompt(context)
            
            async with asyncio.timeout(30):
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
            
            content = response.choices[0].message.content
            # Check if the response contains candidate questions
            if "candidate questions" in content.lower():
                # Extract candidate questions
                candidate_questions = self._extract_candidate_questions(content)
                return {
                    "candidate_questions": candidate_questions,
                    "chart_config": None  # No chart config yet
                }
            
            print(content)
            
            return json.loads(content)
            
        except Exception as e:
            raise ValueError(f"Error generating chart configuration: {str(e)}") from e
    
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
        # Assuming the candidate questions are listed in a specific format
        # This is a simple example; you may need to adjust the parsing logic
        lines = content.splitlines()
        questions = []
        for line in lines:
            if line.strip().startswith("-"):
                questions.append(line.strip()[1:].strip())  # Remove leading '- ' and whitespace
        return questions 