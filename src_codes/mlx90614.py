from adafruit_mlx90614 import MLX90614
import board
import busio
from config import TEMP_OFFSET


class TemperatureSensor:

    def __init__(self):

        self.i2c = busio.I2C(board.SCL, board.SDA)

        self.sensor = MLX90614(self.i2c)

    def read(self):

        temp = self.sensor.object_temperature

        temp -= TEMP_OFFSET

        return round(temp, 1)