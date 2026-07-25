# AI/ML Based Patient Health Monitoring and Alerting Robot Using Raspberry Pi

## Overview

This project is an AI-powered health monitoring system developed using Raspberry Pi 4.

The system continuously monitors:

- Heart Rate (BPM)
- Blood Oxygen Saturation (SpO₂)
- Body Temperature
- ECG Signal

An AI/ML model predicts whether the patient is:

- Normal
- Abnormal
- Critical

The project also provides:

- OLED Displays
- RGB Status LED
- Active Buzzer Alerts
- Local AI Inference
- Dataset Generation

---

## Hardware Used

- Raspberry Pi 4 Model B (8GB)
- MAX30102
- MLX90614
- AD8232 ECG Sensor
- MCP3008 ADC
- SSD1306 OLED
- SH1106 OLED
- RGB LED
- Active Buzzer

---

## Software

- Python 3
- Raspberry Pi OS
- Random Forest Classifier
- Scikit-Learn
- Pandas
- NumPy

---

## Folder Structure

```
AI-Health-Monitor/
│
├── health.py
├── train_model.py
├── predict.py
├── health_dataset.csv
├── health_model.pkl
├── requirements.txt
└── README.md
```

---

## Installation

Clone repository

```
git clone https://github.com/satya-99928/AI-ML-based-health-monitoring-system.git
```

Install packages

```
pip install -r requirements.txt
```

Run

```
python health.py
```

---

## Machine Learning

Algorithm Used:

- Random Forest Classifier

Features

- BPM
- SpO₂
- Temperature
- ECG RMS

Output

- Normal
- Abnormal
- Critical

---

## Authors

- Satyajit Panda

---

## License
Educational purpose only

Academic Project
SOA University
