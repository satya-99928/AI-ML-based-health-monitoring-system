# AI/ML Based Health Monitoring System

A Raspberry Pi–based IoT health monitoring system that measures
- Heart Rate (BPM)
- Blood Oxygen Level (SpO₂)
- Body Temperature
- ECG waveform

The system operates fully offline, logs data locally, and uses machine learning
to predict patient health risk.

## Features
- MAX30102 for BPM & SpO₂
- MLX90614 for body temperature
- AD8232 ECG with waveform display
- Dual OLED display (0.96" + 1.3")
- Local CSV dataset generation
- Machine learning–based risk prediction
- Headless operation (no cloud dependency)

## Hardware Used
- Raspberry Pi
- MAX30102 Pulse Oximeter
- MLX90614 Temperature Sensor
- AD8232 ECG Sensor
- MCP3008 ADC
- OLED Displays (0.96", 1.3")

## Software Stack
- Python
- NumPy, SciPy
- Adafruit CircuitPython Libraries
- Scikit-learn (Random Forest)

## How It Works
1. Sensors collect real-time physiological data
2. Data is processed locally on Raspberry Pi
3. Vitals are displayed on OLED screens
4. Data is stored in CSV format
5. ML model predicts health risk based on trends

## Dataset
The dataset includes:
- BPM
- SpO₂
- Temperature
- ECG Voltage

Stored locally as CSV for model training.

## Machine Learning
- Model: Random Forest Classifier
- Training: Offline using collected dataset
- Inference: Local (no internet required)

## Use Cases
- Home health monitoring
- Elderly care
- Remote clinics
- Academic research

## Authors
- Satyajit Panda
