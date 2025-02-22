# ChatSlide.ai Chart Generator

An AI-powered tool for generating and modifying charts from data files using natural language commands. Features both CLI and web interface for flexible usage.

## Features

### Data Processing
- Support for multiple file formats (CSV, Excel, JSON)
- Automatic data structure analysis
- Smart data transformations (e.g., monthly → quarterly)
- Handles complex data relationships

### Visualization
- Automatic chart type inference
- Multiple chart types (bar, line, pie, scatter, etc.)
- Interactive updates and modifications
- Chart.js-based visualization
- Multi-axis and combined charts

### AI Capabilities
- Natural language command processing
- Context-aware updates
- Topic change detection
- Intelligent data aggregation
- Smart metric calculations

### Interface Options
- Web-based interface with real-time updates
- Command-line interface for automation
- Interactive chart modifications
- Data preview functionality

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd chatslide-ai
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up OpenAI API key:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Usage

### Web Interface

1. Start the server:
```bash
python run.py
```

2. Access the interface:
- Open `http://localhost:8000` in your browser
- Upload data file (CSV, Excel, or JSON)
- Enter natural language commands
- View real-time chart updates

### Command Line Interface

1. Process new file:
```bash
python main.py process-file <file_path> "<command>"
```

2. Update existing chart:
```bash
python main.py update-chart "<command>"
```

### Example Commands

#### Sales Analysis
```bash
# Monthly revenue analysis
python main.py process-file data/sales_data.csv "Show monthly revenue as a bar chart"

# Add comparisons
python main.py update-chart "Add units sold on secondary axis"

# Transform data
python main.py update-chart "Show quarterly totals instead of monthly"

# Change visualization
python main.py update-chart "Make it a stacked bar chart by region"
```

#### Weather Data
```bash
# Temperature analysis
python main.py process-file data/weather_data.xlsx "Plot temperature over time"

# Multiple metrics
python main.py update-chart "Add humidity as line chart"

# Data transformation
python main.py update-chart "Show 7-day moving average"
```

#### Product Performance
```bash
# Metric comparison
python main.py process-file data/product_performance.json "Compare product metrics in radar chart"

# Sales analysis
python main.py update-chart "Show quarterly sales trends"

# Combined visualization
python main.py update-chart "Create bubble chart with satisfaction vs value, sized by sales"
```

## Project Structure

```
chatslide-ai/
├── src/
│   ├── agent/              # AI processing
│   │   ├── chart_agent.py
│   │   └── topic_manager.py
│   ├── api/               # Web API
│   │   └── app.py
│   └── utils/             # Utilities
│       └── file_handler.py
├── static/                # Web assets
│   ├── css/
│   └── js/
├── templates/             # HTML templates
├── data/                  # Example data
├── tests/                 # Test files
├── main.py               # CLI entry
└── run.py                # Web server
```

## Development

### Running Tests
```bash
pytest tests/
```

### Local Development
```bash
# Start server in debug mode
uvicorn src.api.app:app --reload --port 8000
```

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `DEBUG`: Enable debug mode (optional)
- `PORT`: Custom port (optional)

## Troubleshooting

### Common Issues

1. Chart Generation Fails
   - Check data format
   - Verify OpenAI API key
   - Review command syntax

2. Data Processing Issues
   - Ensure correct file format
   - Check data structure
   - Verify file permissions

3. Web Interface Problems
   - Clear browser cache
   - Check console for errors
   - Verify server status

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.
