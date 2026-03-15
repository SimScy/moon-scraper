# Moon Trajectory Dataset Scraper

This project collects and processes **moon position data** from the US Naval Observatory Altitude/Azimuth calculator and builds a **minute-resolution dataset** of the moon’s trajectory in the sky.

The dataset contains:

- Moon altitude
- Moon azimuth
- Illumination (moon phase)
- Timestamp (1-minute resolution)

The data is collected for a specified time range and stored as a structured dataset for analysis and visualization.

---

## Data Source

Data is retrieved from the **US Naval Observatory Altitude/Azimuth calculator**:

https://aa.usno.navy.mil/data/AltAz

Location used in this project:

Munich, Germany  
Latitude: 48.17  
Longitude: 11.50

---

## Project Structure
```
moon-scraper/
│
├─ data/
│ ├─ raw/ # Raw scraped daily tables
│ └─ processed/ # Clean dataset
│
├─ notebooks/
│ └─ showcase.ipynb # Example visualizations
│
├─ scripts/
│ ├─ moon_scraper.py # Selenium scraper
│ └─ moon_merger.py # Data cleaning and aggregation
│
├─ README.md
└─ requirements.txt
```
---

## Data Pipeline

The dataset is generated in two steps.

### 1. Scraping

`moon_scraper.py` retrieves daily tables from the US Naval Observatory Alt/Az calculator using Selenium.

Each day is saved as a raw table file:

    data/raw/datatable_YYYY-MM-DD.txt

---

### 2. Data Processing

`moon_merger.py` performs the following steps:

- loads the raw daily files
- cleans column names
- removes degree symbols
- parses timestamps
- creates a full minute-level time index
- merges all days into a single dataset

The final dataset is saved as:

    data/processed/moon_dataset.csv

---

## Dataset

### 1. Columns

| Column | Description |
|-------|-------------|
| datetime | timestamp |
| Time | original time column |
| Altitude | moon altitude above horizon (degrees) |
| Azimuth | direction in the sky (degrees) |
| Illumination | fraction of the moon illuminated |

### 2. Dataset Preview

Example rows from the generated dataset:

| datetime | Time | Altitude | Azimuth | Illumination |
|----------|------|----------|---------|--------------|
| 2026-04-21 16:49:00 | 16:49 | 68.4 | 203.1 | 0.23 |
| 2026-04-21 16:50:00 | 16:50 | 68.3 | 203.7 | 0.23 |
| 2026-04-21 16:51:00 | 16:51 | 68.3 | 204.2 | 0.23 |
| 2026-04-21 16:52:00 | 16:52 | 68.2 | 204.8 | 0.24 |
| 2026-04-21 16:53:00 | 16:53 | 68.1 | 205.3 | 0.24 |

**Resolution:** 1 minute

---

## Example Visualizations

The notebook `notebooks/showcase.ipynb` demonstrates how to explore the dataset.

Examples include:

- Moon altitude over time
- Moon trajectory in the sky
- Moon phase cycle

---

## Running the Project

### 1. Install dependencies

    pip install -r requirements.txt

### 2. Run the scraper

    python scripts/moon_scraper.py


This will generate raw daily tables in:

    data/raw

### 3. Build the dataset

    python scripts/moon_merger.py


The final dataset will be created in:

    data/processed/moon_dataset.csv

---

## Example Usage

```python
import pandas as pd

df = pd.read_csv("data/processed/moon_dataset.csv")

df["datetime"] = pd.to_datetime(df["datetime"])
df = df.set_index("datetime")

print(df.head())
```

---

## Project purpose

This project is a **small data engineering and web scraping example** demonstrating:

- automated data collection with Selenium
- HTML parsing with BeautifulSoup
- building a structured time-series dataset
- simple data visualization

---

## License

This project is for educational and demonstration purposes.

---