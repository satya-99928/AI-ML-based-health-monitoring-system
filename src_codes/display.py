import board
import busio

import adafruit_ssd1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from luma.core.interface.serial import i2c
from luma.oled.device import sh1106


class Display:

    def __init__(self):

        bus = busio.I2C(
            board.SCL,
            board.SDA
        )

        self.oled = adafruit_ssd1306.SSD1306_I2C(
            128,
            64,
            bus
        )

        self.image = Image.new(
            "1",
            (128, 64)
        )

        self.draw = ImageDraw.Draw(
            self.image
        )

        self.font = ImageFont.load_default()

        serial = i2c(
            port=1,
            address=0x3C
        )

        self.status = sh1106(serial)

    def update_health(
        self,
        bpm,
        spo2,
        temp
    ):

        self.draw.rectangle(
            (0, 0, 128, 64),
            fill=0
        )

        self.draw.text(
            (0, 0),
            f"BPM : {bpm}",
            font=self.font,
            fill=255
        )

        self.draw.text(
            (0, 15),
            f"SpO2 : {spo2}",
            font=self.font,
            fill=255
        )

        self.draw.text(
            (0, 30),
            f"Temp : {temp}",
            font=self.font,
            fill=255
        )

        self.oled.image(self.image)

        self.oled.show()

    def draw_ecg(
        self,
        ecg
    ):

        if len(ecg) < 2:
            return

        mean = sum(ecg) / len(ecg)

        centered = [
            x - mean
            for x in ecg
        ]

        peak = max(
            abs(x)
            for x in centered
        )

        if peak == 0:
            return

        scale = ECG_SCALE / peak

        base = 58

        for i in range(len(centered) - 1):

            y1 = int(
                base -
                centered[i] * scale
            )

            y2 = int(
                base -
                centered[i + 1] * scale
            )

            self.draw.line(
                (
                    i,
                    y1,
                    i + 1,
                    y2
                ),
                fill=255
            )

        self.oled.image(
            self.image
        )

        self.oled.show()