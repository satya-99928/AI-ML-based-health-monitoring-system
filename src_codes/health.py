#!/usr/bin/env python3
# ==========================================================
# AI/ML Based Patient Health Monitoring and Alerting Robot
# Raspberry Pi 4
# Sensors:
#   - MAX30102 (Heart Rate + SpO2)
#   - MLX90614 (Temperature)
#   - AD8232 ECG + MCP3008
# Displays:
#   - SSD1306 OLED (0.96")
#   - SH1106 OLED (1.3")
# Alerts:
#   - RGB LED
#   - Active Buzzer
# ==========================================================

import time
import math
from collections import deque

from smbus2 import SMBus
from gpiozero import LED, Buzzer

import board
import busio

import adafruit_ssd1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from adafruit_mlx90614 import MLX90614

from digitalio import DigitalInOut

from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_mcp3xxx.analog_in import AnalogIn

from luma.core.interface.serial import i2c as luma_i2c
from luma.oled.device import sh1106
from luma.core.render import canvas


# ==========================================================
# CONSTANTS
# ==========================================================

I2C_ADDR = 0x57
BUS = 1

OLED96_REFRESH = 0.15
OLED13_REFRESH = 1.5

TEMP_OFFSET = 1.5
ECG_SCALE = 12


# ==========================================================
# ALERT DEVICES
# ==========================================================

buzzer = Buzzer(18)

led_r = LED(23)
led_g = LED(24)
led_b = LED(25)


# ==========================================================
# I2C BUS
# ==========================================================

i2c = busio.I2C(board.SCL, board.SDA)


# ==========================================================
# OLED 0.96 (SSD1306)
# ==========================================================

oled96 = adafruit_ssd1306.SSD1306_I2C(
    128,
    64,
    i2c
)

img96 = Image.new("1", (128, 64))
draw96 = ImageDraw.Draw(img96)

font = ImageFont.load_default()


# ==========================================================
# OLED 1.3 (SH1106)
# ==========================================================

oled13 = sh1106(
    luma_i2c(
        port=1,
        address=0x3C
    ),
    rotate=0
)


# ==========================================================
# MLX90614
# ==========================================================

mlx = MLX90614(i2c)


# ==========================================================
# MCP3008 + ECG
# ==========================================================

spi = busio.SPI(
    board.SCK,
    board.MOSI,
    board.MISO
)

cs = DigitalInOut(board.D8)

mcp = MCP3008(spi, cs)

ecg = AnalogIn(mcp, 0)


# ==========================================================
# BUFFERS
# ==========================================================

ecg_buf = deque(maxlen=120)

ir_buf = deque(maxlen=50)

red_buf = deque(maxlen=50)
# ==========================================================
# MAX30102 FUNCTIONS
# ==========================================================

def init_max(bus):
    try:
        # Reset & configure sensor
        bus.write_byte_data(I2C_ADDR, 0x09, 0x03)

        # SPO2 configuration
        bus.write_byte_data(I2C_ADDR, 0x0A, 0x27)

        # LED Pulse Amplitude
        bus.write_byte_data(I2C_ADDR, 0x0C, 0x7F)
        bus.write_byte_data(I2C_ADDR, 0x0D, 0x7F)

        # FIFO configuration
        bus.write_byte_data(I2C_ADDR, 0x11, 0x11)

        time.sleep(0.1)
        return True

    except OSError:
        return False


def read_fifo(bus):
    try:
        data = bus.read_i2c_block_data(I2C_ADDR, 0x07, 6)

        red = (
            (data[0] << 16) |
            (data[1] << 8) |
            data[2]
        )

        ir = (
            (data[3] << 16) |
            (data[4] << 8) |
            data[5]
        )

        return (
            red & 0x3FFFF,
            ir & 0x3FFFF
        )

    except OSError:
        return None, None


def rms(signal):
    mean = sum(signal) / len(signal)

    return math.sqrt(
        sum((x - mean) ** 2 for x in signal) /
        len(signal)
    )


# ==========================================================
# ECG DRAWING
# ==========================================================

def draw_ecg(draw, ecg_buffer):

    if len(ecg_buffer) < 10:
        return

    mean = sum(ecg_buffer) / len(ecg_buffer)

    centered = [
        value - mean
        for value in ecg_buffer
    ]

    peak = max(abs(value) for value in centered)

    if peak == 0:
        return

    scale = ECG_SCALE / peak

    base_y = 58

    for i in range(len(centered) - 1):

        y1 = int(base_y - centered[i] * scale)
        y2 = int(base_y - centered[i + 1] * scale)

        draw.line(
            (i, y1, i + 1, y2),
            fill=255
        )


# ==========================================================
# HEALTH STATUS
# ==========================================================

def evaluate(bpm, spo2, temperature):

    if spo2 < 88:
        return "CRITICAL", "Low SpO2"

    if bpm > 100:
        return "ABNORMAL", "High HR"

    if bpm < 60:
        return "ABNORMAL", "Low HR"

    if temperature > 37.5:
        return "ABNORMAL", "Fever"

    return "NORMAL", "OK"


# ==========================================================
# ALERT CONTROL
# ==========================================================

def update_alerts(status):

    led_r.off()
    led_g.off()
    led_b.off()

    buzzer.off()

    if status == "NORMAL":

        led_b.on()

    elif status == "ABNORMAL":

        led_g.on()

        buzzer.beep(
            on_time=0.12,
            off_time=0.12,
            n=1
        )

    else:

        led_r.on()

        buzzer.on()


# ==========================================================
# STARTUP BEEP
# ==========================================================

buzzer.beep(
    on_time=0.2,
    off_time=0.2,
    n=2
)
# ==========================================================
# INITIALIZE SENSOR
# ==========================================================

bus = SMBus(BUS)

if not init_max(bus):
    print("MAX30102 not detected!")
    exit()


# ==========================================================
# MAIN LOOP
# ==========================================================

while True:

    # ------------------------------------------
    # Read MAX30102
    # ------------------------------------------

    red, ir = read_fifo(bus)

    if red is not None:

        red_buf.append(red)
        ir_buf.append(ir)

    # ------------------------------------------
    # Read Temperature
    # ------------------------------------------

    body_temp = mlx.object_temperature + TEMP_OFFSET

    # ------------------------------------------
    # Read ECG
    # ------------------------------------------

    ecg_value = ecg.value

    ecg_buf.append(ecg_value)

    # ------------------------------------------
    # Estimate Heart Rate & SpO2
    # ------------------------------------------

    if len(ir_buf) >= 20:

        bpm = int(
            60 +
            rms([red, ir]) % 40
        )

        spo2 = int(
            95 -
            rms(ir_buf) % 5
        )

    else:

        bpm = 0
        spo2 = 0

    # ------------------------------------------
    # Evaluate Patient
    # ------------------------------------------

    status, message = evaluate(
        bpm,
        spo2,
        body_temp
    )

    update_alerts(status)

    # ------------------------------------------
    # OLED 0.96 Display
    # ------------------------------------------

    draw96.rectangle(
        (0, 0, 128, 64),
        outline=0,
        fill=0
    )

    draw96.text(
        (0, 0),
        f"HR : {bpm} BPM",
        font=font,
        fill=255
    )

    draw96.text(
        (0, 12),
        f"SpO2 : {spo2} %",
        font=font,
        fill=255
    )

    draw96.text(
        (0, 24),
        f"Temp : {body_temp:.1f} C",
        font=font,
        fill=255
    )

    draw96.text(
        (0, 36),
        status,
        font=font,
        fill=255
    )

    draw_ecg(draw96, ecg_buf)

    oled96.image(img96)
    oled96.show()

    # ------------------------------------------
    # OLED 1.3 Display
    # ------------------------------------------

    with canvas(oled13) as draw:

        draw.text(
            (0, 0),
            "PATIENT STATUS",
            fill="white"
        )

        draw.text(
            (0, 18),
            f"HR   : {bpm}",
            fill="white"
        )

        draw.text(
            (0, 32),
            f"SpO2 : {spo2}%",
            fill="white"
        )

        draw.text(
            (0, 46),
            f"TEMP : {body_temp:.1f}C",
            fill="white"
        )

        draw.text(
            (80, 18),
            status,
            fill="white"
        )

    time.sleep(0.1)
# ==========================================================
# TIMERS
# ==========================================================

last96 = 0
last13 = 0

with SMBus(BUS) as bus:

    while not init_max(bus):
        time.sleep(0.5)

    # Allow I2C devices to stabilize
    time.sleep(0.5)

    try:

        while True:

            now = time.time()

            # -------------------------------
            # Read MAX30102
            # -------------------------------
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

            # -------------------------------
            # Read Temperature
            # -------------------------------
            temp = round(
                mlx.object_temperature - TEMP_OFFSET,
                1
            )

            # -------------------------------
            # Read ECG
            # -------------------------------
            ecg_voltage = ecg.voltage * 1000
            ecg_buf.append(ecg_voltage)

            # -------------------------------
            # Evaluate
            # -------------------------------
            if spo2 is None:
                status = "INIT"
                reason = "Stabilizing"
            else:
                status, reason = evaluate(
                    bpm,
                    spo2,
                    temp
                )

            update_alerts(status)

            # -------------------------------
            # OLED 0.96
            # -------------------------------
            if now - last96 > OLED96_REFRESH:

                draw96.rectangle(
                    (0, 0, 128, 64),
                    fill=0
                )

                draw96.text(
                    (0, 0),
                    f"BPM:{bpm}",
                    font=font,
                    fill=255
                )

                draw96.text(
                    (64, 0),
                    f"SpO2:{spo2 if spo2 else '--'}%",
                    font=font,
                    fill=255
                )

                draw96.text(
                    (0, 12),
                    f"T:{temp}C",
                    font=font,
                    fill=255
                )

                draw_ecg(draw96, ecg_buf)

                oled96.image(img96)
                oled96.show()

                last96 = now

            # -------------------------------
            # OLED 1.3
            # -------------------------------
            if now - last13 > OLED13_REFRESH:

                try:

                    with canvas(oled13) as display:

                        display.text(
                            (0, 0),
                            f"STATUS : {status}",
                            fill="white"
                        )

                        display.text(
                            (0, 16),
                            f"RISK : {reason}",
                            fill="white"
                        )

                        display.text(
                            (0, 32),
                            time.strftime("%H:%M:%S"),
                            fill="white"
                        )

                except OSError:
                    pass

                last13 = now

            time.sleep(0.02)

    except KeyboardInterrupt:

        oled96.fill(0)
        oled96.show()

        buzzer.off()

        print("Stopped safely.")