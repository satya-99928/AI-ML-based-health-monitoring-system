# ecg.py
# AD8232 ECG reader using MCP3008

import board
import busio
from digitalio import DigitalInOut
from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_mcp3xxx.analog_in import AnalogIn

class ECGSensor:
    def __init__(self):
        spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        cs = DigitalInOut(board.D8)
        self.mcp = MCP3008(spi, cs)
        self.channel = AnalogIn(self.mcp, 0)

    def read_voltage(self):
        return round(self.channel.voltage, 4)
