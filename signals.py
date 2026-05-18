import csv
import json
import subprocess
import matplotlib.pyplot as plt

if __name__ == "__main__":
    subprocess.run(["./dsp.exe"], check=True)

    with open("quantization_mse.json", 'r') as file:
        data = json.load(file)

    mse = data["quantization_mse"]

    fig = plt.figure(figsize=(16, 16))
    ax = fig.add_subplot(111)

    df = {
        "signal_samples" : []
        , "quantization_samples" : []
        , "time_samples": []
    }

    with open(f"signal_and_quantization_samples.csv", 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            for key in df.keys():
                df[key].append(float(row[key]))

    ax.plot(df["time_samples"], df["signal_samples"], color="blue", label="signal samples")
    ax.plot(df["time_samples"], df["quantization_samples"], color="red", label="quantization samples")

    ax.set_title(f"signal and quantization samples (mse = {mse})", fontsize=20)
    ax.set_xlabel("time, s", fontsize=18)
    ax.set_ylabel("samples", fontsize=18)
    ax.legend(fontsize=15)
    ax.grid()

    fig.savefig("signal_and_quantization.png")
