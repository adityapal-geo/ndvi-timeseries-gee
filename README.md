# ndvi-timeseries-gee
NDVI Time-Series Analysis (2004–2025) using Landsat &amp; Google Earth Engine


# NDVI Time-Series Analysis (2004–2025)

A complete vegetation monitoring workflow using **Normalized Difference Vegetation Index (NDVI)** derived from Landsat imagery in Google Earth Engine (GEE).  
This project visualizes long-term vegetation dynamics through an animated time series.

---

## Overview

This study analyzes yearly NDVI trends from 2004 to 2025 to understand vegetation changes over time.  
It integrates multi-sensor satellite data and produces a clean animation for interpretation and presentation.

---

## Study Area

- Custom Area of Interest (AOI) uploaded to GEE Assets  
- Can be adapted to any region  

---

## Data Sources

- Landsat 5 (2004–2012)  
- Landsat 8 (2013–2025)  

Source: USGS / Google Earth Engine  

---

## Methodology

NDVI is calculated as:

NDVI = (NIR - Red) / (NIR + Red)

### Workflow Steps:
1. Load AOI from GEE Assets  
2. Filter Landsat collections by date & region  
3. Apply cloud masking using QA_PIXEL band  
4. Compute NDVI:
   - Landsat 5 → (SR_B4, SR_B3)  
   - Landsat 8 → (SR_B5, SR_B4)  
5. Generate annual mean NDVI  
6. Normalize values using percentile stretch (2–98%)  
7. Export thumbnails via GEE  
8. Create animation using Python  

---

## Outputs

### 🔹 NDVI Time-Series Animation
![NDVI Animation](ndvi_2004_2025.gif)

---

### Grid Preview
![NDVI Grid](ndvi_grid_preview.png)

---

## Tech Stack

- Google Earth Engine (Python API)  
- NumPy  
- Matplotlib  
- Pillow (PIL)  
- Requests  
- ImageIO / FFmpeg  

---

## Applications

- Vegetation monitoring  
- Drought assessment  
- Urban expansion analysis  
- Land Use / Land Cover (LULC) studies  
- Climate change impact analysis  

---

## How to Run

1. Install dependencies:
pip install earthengine-api matplotlib imageio pillow requests

2. Authenticate GEE:
import ee  
ee.Authenticate()  
ee.Initialize()  

3. Run the script:
python ndvi_animation.py  

---

## Key Insights

- Detects vegetation increase/decrease over time  
- Highlights environmental and land-use changes  
- Useful for academic research and geospatial analysis  

---

## Author

Aditya Pal  



