import joblib
import pandas as pd

# Load trained model
model = joblib.load("health_model.pkl")


def predict_health(bpm, spo2, temperature, ecg_rms):

    sample = pd.DataFrame({
        "BPM": [bpm],
        "SpO2": [spo2],
        "Temperature": [temperature],
        "ECG_RMS": [ecg_rms]
    })

    prediction = model.predict(sample)[0]

    return prediction


if __name__ == "__main__":

    bpm = float(input("Heart Rate (BPM): "))
    spo2 = float(input("SpO2 (%): "))
    temperature = float(input("Temperature (°C): "))
    ecg_rms = float(input("ECG RMS: "))

    result = predict_health(
        bpm,
        spo2,
        temperature,
        ecg_rms
    )

    print("\nPredicted Health Status:", result)