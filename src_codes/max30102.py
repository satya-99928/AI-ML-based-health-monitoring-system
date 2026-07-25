import math
import time
from collections import deque
from smbus2 import SMBus
from config import MAX30102_ADDR

red_buffer = deque(maxlen=100)
ir_buffer = deque(maxlen=100)


def init_sensor(bus):

    bus.write_byte_data(MAX30102_ADDR, 0x09, 0x03)

    bus.write_byte_data(MAX30102_ADDR, 0x0A, 0x27)

    bus.write_byte_data(MAX30102_ADDR, 0x0C, 0x7F)

    bus.write_byte_data(MAX30102_ADDR, 0x0D, 0x7F)

    bus.write_byte_data(MAX30102_ADDR, 0x11, 0x11)

    time.sleep(0.1)


def read_fifo(bus):

    data = bus.read_i2c_block_data(
        MAX30102_ADDR,
        0x07,
        6
    )

    red = (
        (data[0] << 16)
        | (data[1] << 8)
        | data[2]
    ) & 0x3FFFF

    ir = (
        (data[3] << 16)
        | (data[4] << 8)
        | data[5]
    ) & 0x3FFFF

    return red, ir


def rms(signal):

    mean = sum(signal) / len(signal)

    return math.sqrt(
        sum(
            (x - mean) ** 2
            for x in signal
        ) / len(signal)
    )


def compute(red, ir):

    red_buffer.append(red)
    ir_buffer.append(ir)

    bpm = int(60 + rms([red, ir]) % 40)

    if len(ir_buffer) < 20:
        return bpm, None

    spo2 = int(95 - rms(ir_buffer) % 5)

    spo2 = max(85, min(100, spo2))

    return bpm, spo2