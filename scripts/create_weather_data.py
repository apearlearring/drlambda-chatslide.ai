import pandas as pd
import numpy as np

# Create sample weather data
dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
np.random.seed(42)

data = {
    'Date': dates,
    'Temperature': np.random.normal(20, 5, len(dates)),  # Mean 20°C, std 5°C
    'Humidity': np.random.normal(60, 10, len(dates)),    # Mean 60%, std 10%
    'Rainfall': np.random.exponential(2, len(dates)),    # Exponential distribution
    'Wind_Speed': np.random.normal(15, 5, len(dates))    # Mean 15km/h, std 5km/h
}

df = pd.DataFrame(data)
df['Temperature'] = df['Temperature'].round(1)
df['Humidity'] = df['Humidity'].round(1)
df['Rainfall'] = df['Rainfall'].round(2)
df['Wind_Speed'] = df['Wind_Speed'].round(1)

# Save to Excel
df.to_excel('data/weather_data.xlsx', index=False) 