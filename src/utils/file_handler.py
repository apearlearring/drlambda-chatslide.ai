import pandas as pd
import json
from pathlib import Path
from typing import Any, Union
import shutil

class FileHandler:
    def __init__(self):
        self.supported_extensions = {'.csv', '.xlsx', '.json'}
        self.output_dir = Path('output')
        self.template_dir = Path('templates')
        
    def load_file(self, file_path: str) -> Any:
        """
        Load and parse input file
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if path.suffix not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {path.suffix}")
            
        try:
            if path.suffix == '.json':
                with open(path, 'r') as f:
                    return json.load(f)
            elif path.suffix == '.csv':
                return pd.read_csv(path)
            elif path.suffix == '.xlsx':
                return pd.read_excel(path)
        except Exception as e:
            raise ValueError(f"Error loading file: {str(e)}")
    
    def save_chart(self, chart_config: dict) -> str:
        """
        Save chart configuration and generate HTML
        """
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)
        
        # Save chart configuration
        config_path = self.output_dir / 'chart_config.json'
        with open(config_path, 'w') as f:
            json.dump(chart_config, f, indent=2)
        
        # Generate HTML file
        html_path = self.output_dir / 'chart.html'
        self._generate_html(chart_config, html_path)
        
        return str(html_path)
    
    def _generate_html(self, chart_config: dict, output_path: Path):
        """
        Generate HTML file with Chart.js visualization
        """
        template_path = self.template_dir / 'chart.html'
        
        # Create template if it doesn't exist
        if not template_path.exists():
            self._create_template()
        
        # Read template and replace placeholder with chart configuration
        with open(template_path, 'r') as f:
            template = f.read()
        
        html_content = template.replace('{{CHART_CONFIG}}', json.dumps(chart_config))
        
        with open(output_path, 'w') as f:
            f.write(html_content)
    
    def _create_template(self):
        """
        Create basic Chart.js template
        """
        self.template_dir.mkdir(exist_ok=True)
        template_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Chart Visualization</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <canvas id="myChart"></canvas>
    <script>
        const config = {{CHART_CONFIG}};
        new Chart(document.getElementById('myChart'), config);
    </script>
</body>
</html>
"""
        with open(self.template_dir / 'chart.html', 'w') as f:
            f.write(template_content) 