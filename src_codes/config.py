"""
Project Configuration
AI/ML Patient Health Monitoring Robot
"""

# ===========================
# I2C Addresses
# ===========================

MAX30102_ADDR = 0x57
MLX90614_ADDR = 0x5A

# ===========================
# Raspberry Pi GPIO
# ===========================

RED_LED = 23
GREEN_LED = 24
BLUE_LED = 25

BUZZER = 18

# ===========================
# SPI Pins (MCP3008)
# ===========================

SPI_CHANNEL = 0

ECG_CHANNEL = 0

# ===========================
# OLED
# ===========================

SSD1306_WIDTH = 128
SSD1306_HEIGHT = 64

SH1106_WIDTH = 128
SH1106_HEIGHT = 64

OLED96_REFRESH = 0.15
OLED13_REFRESH = 1.5

# ===========================
# Temperature
# ===========================

TEMP_OFFSET = 1.5

NORMAL_TEMP = 37.5

# ===========================
# Heart Rate
# ===========================

MIN_BPM = 60
MAX_BPM = 100

# ===========================
# SpO2
# ===========================

MIN_SPO2 = 90
CRITICAL_SPO2 = 88

# ===========================
# ECG
# ===========================

ECG_SCALE = 12

ECG_BUFFER = 120

# ===========================
# MAX30102
# ===========================

PPG_BUFFER = 100

SAMPLE_RATE = 100

# ===========================
# Dataset
# ===========================

DATASET_FILE = "../ml/dataset.csv"

MODEL_FILE = "../ml/model.pkl"

# ===========================
# Status
# ===========================

NORMAL = "NORMAL"
ABNORMAL = "ABNORMAL"
CRITICAL = "CRITICAL"
INIT = "INIT"