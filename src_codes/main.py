import time
import joblib
import pandas as pd
from smbus2 import SMBus

from max30102 import init_sensor, read_fifo, compute
from mlx90614 import TemperatureSensor
from ecg import ECGSensor
from display import Display
from alerts import AlertSystem
from dataset_logger import DatasetLogger

from config import MODEL_FILE


def predict(model, bpm, spo2, temp, ecg):

    data = pd.DataFrame([{
        "BPM": bpm,
        "SpO2": spo2,
        "Temperature": temp,
        "ECG_RMS": ecg
    }])

    return model.predict(data)[0]


def main():

    print("=" * 50)
    print("AI/ML Patient Health Monitoring Robot")
    print("=" * 50)

    model = joblib.load(MODEL_FILE)

    bus = SMBus(1)

    init_sensor(bus)

    temp_sensor = TemperatureSensor()

    ecg_sensor = ECGSensor()

    display = Display()

    alerts = AlertSystem()

    logger = DatasetLogger()

    while True:

        red, ir = read_fifo(bus)

        bpm, spo2 = compute(red, ir)

        if spo2 is None:
            continue

        temperature = temp_sensor.read()

        ecg_sensor.read()

        ecg_rms = ecg_sensor.rms()

        status = predict(
            model,
            bpm,
            spo2,
            temperature,
            ecg_rms
        )

        display.update_health(
            bpm,
            spo2,
            temperature
        )

        display.draw_ecg(
            ecg_sensor.waveform()
        )

        alerts.update(status)

        logger.save(
            bpm,
            spo2,
            temperature,
            ecg_rms,
            status
        )

        print(
            f"BPM:{bpm}  "
            f"SpO₂:{spo2}%  "
            f"Temp:{temperature}°C  "
            f"ECG:{ecg_rms:.2f}  "
            f"Status:{status}"
        )

        time.sleep(0.1)


if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:

        print("\nSystem Stopped.")