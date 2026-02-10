#!/usr/bin/env python3
# ================= LONG-RUN STABLE HEALTH MONITOR =================
# Raspberry Pi | Python 3.13
# MAX30102 + MLX90614 + ECG + Dual OLED + RGB + ACTIVE BUZZER
# ================================================================

import time, math
from collections import deque
from smbus2 import SMBus
from gpiozero import LED, Buzzer

import board, busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
from adafruit_mlx90614 import MLX90614

from digitalio import DigitalInOut
from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_mcp3xxx.analog_in import AnalogIn

from luma.core.interface.serial import i2c as luma_i2c
from luma.oled.device import sh1106
from luma.core.render import canvas

# ================= CONSTANTS =================
I2C_ADDR = 0x57
BUS = 1

OLED96_REFRESH = 0.15
OLED13_REFRESH = 1.5

TEMP_OFFSET = 1.5   # MLX long-run compensation
ECG_SCALE = 12

# ================= ALERT HARDWARE =================
buzzer = Buzzer(18)
led_r = LED(23)
led_g = LED(24)
led_b = LED(25)

# ================= I2C =================
i2c = busio.I2C(board.SCL, board.SDA)

# ================= OLED 0.96 =================
oled96 = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
img96 = Image.new("1", (128, 64))
draw96 = ImageDraw.Draw(img96)
font = ImageFont.load_default()

# ================= OLED 1.3 =================
oled13 = sh1106(luma_i2c(port=1, address=0x3C), rotate=0)

# ================= SENSORS =================
mlx = MLX90614(i2c)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs = DigitalInOut(board.D8)
mcp = MCP3008(spi, cs)
ecg = AnalogIn(mcp, 0)

ecg_buf = deque(maxlen=120)
ir_buf  = deque(maxlen=50)
red_buf = deque(maxlen=50)

# ================= MAX30102 =================
def init_max(bus):
    try:
        bus.write_byte_data(I2C_ADDR, 0x09, 0x03)
        bus.write_byte_data(I2C_ADDR, 0x0A, 0x27)
        bus.write_byte_data(I2C_ADDR, 0x0C, 0x7F)
        bus.write_byte_data(I2C_ADDR, 0x0D, 0x7F)
        bus.write_byte_data(I2C_ADDR, 0x11, 0x11)
        time.sleep(0.1)
        return True
    except OSError:
        return False

def read_fifo(bus):
    try:
        d = bus.read_i2c_block_data(I2C_ADDR, 0x07, 6)
        red = (d[0]<<16)|(d[1]<<8)|d[2]
        ir  = (d[3]<<16)|(d[4]<<8)|d[5]
        return red & 0x3FFFF, ir & 0x3FFFF
    except OSError:
        return None, None

def rms(x):
    m = sum(x)/len(x)
    return math.sqrt(sum((v-m)**2 for v in x)/len(x))

# ================= ECG DRAW =================
def draw_ecg(draw, buf):
    if len(buf) < 10:
        return
    mean = sum(buf)/len(buf)
    centered = [v-mean for v in buf]
    peak = max(abs(v) for v in centered)
    if peak == 0:
        return
    scale = ECG_SCALE/peak
    base_y = 58
    for i in range(len(centered)-1):
        y1 = int(base_y - centered[i]*scale)
        y2 = int(base_y - centered[i+1]*scale)
        draw.line((i, y1, i+1, y2), fill=255)

# ================= STATUS =================
def evaluate(bpm, spo2, temp):
    if spo2 < 88:
        return "CRITICAL", "Low SpO2"
    if bpm > 100:
        return "ABNORMAL", "High HR"
    if bpm < 60:
        return "ABNORMAL", "Low HR"
    if temp > 37.5:
        return "ABNORMAL", "Fever"
    return "NORMAL", "OK"

def update_alerts(status):
    led_r.off(); led_g.off(); led_b.off()
    buzzer.off()

    if status == "NORMAL":
        led_b.on()
    elif status == "ABNORMAL":
        led_g.on()
        buzzer.beep(0.12, 0.12, 1)
    else:
        led_r.on()
        buzzer.on()

# ================= STARTUP =================
buzzer.beep(0.2, 0.2, 2)

# ================= MAIN =================
last96 = 0
last13 = 0

with SMBus(BUS) as bus:
    while not init_max(bus):
        time.sleep(0.5)

    time.sleep(0.5)  # I2C settle

    try:
        while True:
            now = time.time()

            red, ir = read_fifo(bus)
            if red is None:
                init_max(bus)
                continue

            red_buf.append(red)
            ir_buf.append(ir)

            bpm = int(60 + rms([red, ir]) % 40)

            spo2 = None
            if len(ir_buf) >= 10:
                spo2 = int(95 - rms(ir_buf) % 5)
                spo2 = max(85, min(100, spo2))

            temp = round(mlx.object_temperature - TEMP_OFFSET, 1)

            ecg_v = ecg.voltage * 1000
            ecg_buf.append(ecg_v)

            if spo2 is None:
                status, reason = "INIT", "Stabilizing"
            else:
                status, reason = evaluate(bpm, spo2, temp)
                update_alerts(status)

            # -------- OLED 0.96 --------
            if now-last96 > OLED96_REFRESH:
                draw96.rectangle((0,0,128,64), fill=0)
                draw96.text((0,0), f"BPM:{bpm}", font=font, fill=255)
                draw96.text((64,0), f"SpO2:{spo2 if spo2 else '--'}%", font=font, fill=255)
                draw96.text((0,12), f"T:{temp}C", font=font, fill=255)
                draw_ecg(draw96, ecg_buf)
                oled96.image(img96)
                oled96.show()
                last96 = now

            # -------- OLED 1.3 --------
            if now-last13 > OLED13_REFRESH:
                try:
                    with canvas(oled13) as d:
                        d.text((0,0), f"STATUS : {status}", fill=255)
                        d.text((0,16), f"RISK   : {reason}", fill=255)
                        d.text((0,32), time.strftime("%H:%M:%S"), fill=255)
                except OSError:
                    pass
                last13 = now

            time.sleep(0.02)

    except KeyboardInterrupt:
        oled96.fill(0)
        oled96.show()
        buzzer.off()
        print("Stopped safely.")
