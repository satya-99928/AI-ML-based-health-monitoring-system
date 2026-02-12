# mlx.py
# MLX90614 temperature sensor module

import board
import busio
from adafruit_mlx90614 import MLX90614

class TemperatureSensor:
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = MLX90614(i2c)

    def read_temperature(self):
        return round(self.sensor.object_temperature, 2)
