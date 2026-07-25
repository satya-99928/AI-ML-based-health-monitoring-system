import board
import busio

from digitalio import DigitalInOut

from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_mcp3xxx.analog_in import AnalogIn

from collections import deque

from config import ECG_SCALE
from config import ECG_BUFFER


class ECGSensor:

    def __init__(self):

        spi = busio.SPI(
            board.SCK,
            board.MOSI,
            board.MISO
        )

        cs = DigitalInOut(board.D8)

        mcp = MCP3008(
            spi,
            cs
        )

        self.channel = AnalogIn(
            mcp,
            0
        )

        self.buffer = deque(
            maxlen=ECG_BUFFER
        )

    def read(self):

        value = self.channel.voltage * 1000

        self.buffer.append(value)

        return value

    def waveform(self):

        return list(self.buffer)

    def rms(self):

        if len(self.buffer) == 0:
            return 0

        mean = sum(self.buffer) / len(self.buffer)

        return (
            sum(
                (x - mean) ** 2
                for x in self.buffer
            ) / len(self.buffer)
        ) ** 0.5