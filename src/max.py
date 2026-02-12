#!/usr/bin/env python3
# MAX30102 FIFO → BPM & SpO2 → OLED DISPLAY
# VERIFIED WORKING VERSION

import time
from collections import deque
import math
from smbus2 import SMBus

# Optional numpy/scipy
try:
    import numpy as np
except Exception:
    np = None

try:
    from scipy.signal import butter, filtfilt
    SCIPY_OK = True
except Exception:
    SCIPY_OK = False

# OLED
import board, busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

# ---------- CONSTANTS ----------
I2C_ADDR = 0x57
BUS = 1

# ---------- OLED INIT ----------
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)
image = Image.new("1", (128, 64))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

# ---------- FIFO READ ----------
def read_fifo_sample(bus):
    data = bus.read_i2c_block_data(I2C_ADDR, 0x07, 6)
    red = (data[0] << 16) | (data[1] << 8) | data[2]
    ir  = (data[3] << 16) | (data[4] << 8) | data[5]
    return red & 0x3FFFF, ir & 0x3FFFF

# ---------- SIGNAL HELPERS ----------
def rms(x):
    m = sum(x)/len(x)
    return math.sqrt(sum((v-m)**2 for v in x)/len(x))

def bandpass_simple(x, fs, low=0.7, high=4.0):
    if np is not None and SCIPY_OK:
        b,a = butter(3, [low/(0.5*fs), high/(0.5*fs)], btype='band')
        return filtfilt(b,a, np.asarray(x, float))
    else:
        return [v - (sum(x)/len(x)) for v in x]

def detect_peaks_simple(sig, fs, min_distance_sec=0.35):
    if len(sig) < 3:
        return []
    min_dist = int(min_distance_sec * fs)
    peaks = []
    for i in range(1, len(sig)-1):
        if sig[i] > sig[i-1] and sig[i] >= sig[i+1]:
            if not peaks or (i - peaks[-1] >= min_dist):
                peaks.append(i)
    return peaks

def compute_hr_spo2(ir_buf, red_buf, fs):
    if len(ir_buf) < int(3 * fs):
        return 0.0, 0.0, 0.0

    ir_f = bandpass_simple(list(ir_buf), fs)
    red_f = bandpass_simple(list(red_buf), fs)

    peaks = detect_peaks_simple(ir_f, fs)
    bpm = 0.0
    if len(peaks) >= 2:
        intervals = [(peaks[i+1]-peaks[i]) / fs for i in range(len(peaks)-1)]
        bpm = 60.0 / sorted(intervals)[len(intervals)//2]

    ac_ir = rms(ir_f)
    ac_red = rms(red_f)
    dc_ir = sum(ir_buf)/len(ir_buf)
    dc_red = sum(red_buf)/len(red_buf)

    spo2 = 0.0
    if ac_ir > 0:
        R = (ac_red/dc_red) / (ac_ir/dc_ir)
        spo2 = 110 - 25 * R
        spo2 = max(50, min(100, spo2))

    q = 1.0
    return round(bpm,1), round(spo2,1), q

# ---------- MAIN ----------
def main():
    display_bpm = 0.0
    display_spo2 = 0.0

    with SMBus(BUS) as bus:
        # Sensor init
        bus.write_byte_data(I2C_ADDR, 0x09, 0x03)
        bus.write_byte_data(I2C_ADDR, 0x0A, 0x27)
        bus.write_byte_data(I2C_ADDR, 0x0C, 0x7F)
        bus.write_byte_data(I2C_ADDR, 0x0D, 0x7F)
        bus.write_byte_data(I2C_ADDR, 0x11, 0x11)

        # Measure sampling rate
        ts = []
        for _ in range(60):
            read_fifo_sample(bus)
            ts.append(time.time())
            time.sleep(0.005)

        fs = 1 / (sum(ts[i+1]-ts[i] for i in range(len(ts)-1)) / (len(ts)-1))
        fs = round(fs, 2)
        print("Measured fs:", fs)

        ir_q = deque(maxlen=int(8 * fs))
        red_q = deque(maxlen=int(8 * fs))

        print("Running...")

        while True:
            r, ir = read_fifo_sample(bus)
            red_q.append(r)
            ir_q.append(ir)

            if len(ir_q) >= int(3 * fs):
                bpm, spo2, q = compute_hr_spo2(ir_q, red_q, fs)

                if bpm > 30 and spo2 > 70:
                    display_bpm = bpm
                    display_spo2 = spo2

                # Terminal
                print(time.strftime("%H:%M:%S"),
                      f"BPM:{display_bpm:5.1f} SpO2:{display_spo2:5.1f}%",
                      end="\r")

                # OLED
                draw.rectangle((0,0,128,64), fill=0)
                draw.text((0, 0),  f"BPM : {display_bpm:5.1f}", font=font, fill=255)
                draw.text((0, 24), f"SpO2: {display_spo2:5.1f} %", font=font, fill=255)
                oled.image(image)
                oled.show()

            time.sleep(0.01)

if __name__ == "__main__":
    main()
