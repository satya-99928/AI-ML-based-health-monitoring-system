import csv
import os

from config import DATASET_FILE


class DatasetLogger:

    def __init__(self):

        if not os.path.exists(DATASET_FILE):

            with open(DATASET_FILE, "w", newline="") as file:

                writer = csv.writer(file)

                writer.writerow([
                    "BPM",
                    "SpO2",
                    "Temperature",
                    "ECG_RMS",
                    "Status"
                ])

    def save(
        self,
        bpm,
        spo2,
        temp,
        ecg,
        status
    ):

        with open(DATASET_FILE, "a", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                bpm,
                spo2,
                temp,
                round(ecg, 2),
                status
            ])