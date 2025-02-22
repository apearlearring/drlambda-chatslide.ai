import pandas as pd
import numpy as np
import json
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    Path('data').mkdir(exist_ok=True)

def generate_sales_data():
    """Generate and save sales data CSV"""
    sales_data = """Month,Revenue,Units_Sold,Region
Jan-2023,45000,120,North
Feb-2023,52000,140,North
Mar-2023,58000,155,North
Apr-2023,61000,165,South
May-2023,72000,190,South
Jun-2023,68000,175,South
Jul-2023,75000,200,East
Aug-2023,82000,220,East
Sep-2023,79000,210,East
Oct-2023,85000,230,West
Nov-2023,92000,250,West
Dec-2023,98000,270,West"""
    
    with open('data/sales_data.csv', 'w') as f:
        f.write(sales_data)

def generate_weather_data():
    """Generate and save weather data Excel"""
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    np.random.seed(42)

    data = {
        'Date': dates,
        'Temperature': np.random.normal(20, 5, len(dates)),
        'Humidity': np.random.normal(60, 10, len(dates)),
        'Rainfall': np.random.exponential(2, len(dates)),
        'Wind_Speed': np.random.normal(15, 5, len(dates))
    }

    df = pd.DataFrame(data)
    df['Temperature'] = df['Temperature'].round(1)
    df['Humidity'] = df['Humidity'].round(1)
    df['Rainfall'] = df['Rainfall'].round(2)
    df['Wind_Speed'] = df['Wind_Speed'].round(1)

    df.to_excel('data/weather_data.xlsx', index=False)

def generate_product_data():
    """Generate and save product performance JSON"""
    product_data = {
        "products": [
            {
                "name": "Laptop Pro",
                "metrics": {
                    "satisfaction": 4.5,
                    "reliability": 4.2,
                    "performance": 4.8,
                    "value": 3.9,
                    "design": 4.6
                },
                "sales_by_quarter": [
                    {"quarter": "Q1", "units": 1200},
                    {"quarter": "Q2", "units": 1450},
                    {"quarter": "Q3", "units": 1800},
                    {"quarter": "Q4", "units": 2100}
                ]
            },
            {
                "name": "Tablet X",
                "metrics": {
                    "satisfaction": 4.3,
                    "reliability": 4.4,
                    "performance": 4.1,
                    "value": 4.5,
                    "design": 4.7
                },
                "sales_by_quarter": [
                    {"quarter": "Q1", "units": 2300},
                    {"quarter": "Q2", "units": 2500},
                    {"quarter": "Q3", "units": 2800},
                    {"quarter": "Q4", "units": 3200}
                ]
            },
            {
                "name": "Smartphone Y",
                "metrics": {
                    "satisfaction": 4.6,
                    "reliability": 4.3,
                    "performance": 4.5,
                    "value": 4.2,
                    "design": 4.8
                },
                "sales_by_quarter": [
                    {"quarter": "Q1", "units": 5200},
                    {"quarter": "Q2", "units": 5800},
                    {"quarter": "Q3", "units": 6300},
                    {"quarter": "Q4", "units": 7100}
                ]
            }
        ]
    }
    
    with open('data/product_performance.json', 'w') as f:
        json.dump(product_data, f, indent=2)

def main():
    """Generate all test data"""
    create_directories()
    generate_sales_data()
    generate_weather_data()
    generate_product_data()
    print("Test data generated successfully!")

if __name__ == "__main__":
    main() 