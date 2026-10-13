# SIT225 Task 5C – Accelerometer Dashboard

## Project Overview

This project uses Python and Plotly Dash to visualise accelerometer readings collected from an iPhone.

The dashboard displays acceleration along three axes (X, Y, and Z) using an interactive graph.

## Technologies Used

- Python
- Plotly Dash
- Pandas
- Arduino IoT Cloud
- iPhone accelerometer

## Features

- Visualisation of real accelerometer measurements
- Smooth playback of 499 recorded samples
- Interactive X, Y, and Z acceleration graph
- Reusable Python code for updating the dashboard

## How to Run

1. Install the required libraries:

   `pip install dash plotly pandas`

2. Place the Python script and CSV data file in the same folder.
3. Run the Python script:

   `python SIT225_Task5C_Real_Dash.py`

4. Open `http://127.0.0.1:8050/` in your browser.

## Implementation Status

The dashboard successfully displays real accelerometer measurements previously recorded from an iPhone.

Live streaming from Arduino IoT Cloud to Python was attempted but was not successfully established. The current implementation replays recorded sensor data rather than receiving continuous live updates.

## Author

SIT225 Student – Deakin University
