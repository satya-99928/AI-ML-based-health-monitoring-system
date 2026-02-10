# AI/ML Based Health Monitoring System

## Overview
This project implements a headless IoT-based health monitoring system using a Raspberry Pi. The system continuously measures heart rate, blood oxygen saturation (SpO₂), body temperature, and ECG signals, processes the data locally, logs it for analysis, and applies machine learning to assess patient health status.

## Hardware Components
- Raspberry Pi 4
- MAX30102 (Heart Rate & SpO₂ Sensor)
- AD8232 ECG Sensor
- MCP3008 ADC
- MLX90614 Temperature Sensor
- 0.96" OLED Display (Vitals & ECG waveform)
- 1.3" OLED Display (Health status & risk)

## Software & Tools
- Python
- Raspberry Pi OS (Headless)
- Adafruit CircuitPython Libraries
- NumPy, SciPy
- Pandas
- Scikit-learn (Random Forest)

## Features
- Real-time vital sign monitoring
- ECG waveform visualization
- Dual OLED display architecture
- CSV-based data logging
- Machine learning-based health status prediction
- Fully headless operation

## Machine Learning
A Random Forest classifier is trained on extracted physiological features to classify patient health conditions as Normal, Warning, or Critical.

## Deployment
The system runs autonomously on Raspberry Pi after initial setup. No web application, mobile app, or cloud services are used.

## License
This project is for academic use.
## Important Files
[randon_forest_train.py](https://github.com/user-attachments/files/25202475/randon_forest_train.py)
[health.py](https://github.com/user-attachments/files/25202486/health.py)
## Demo Video
https://youtu.be/D8LGl8KfOSI
