import csv
import subprocess
import matplotlib.pyplot as plt

if __name__ == "__main__":
    subprocess.run(["./dsp.exe"], check=True)

    fig = plt.figure(figsize=(16, 16))
    ax = fig.add_subplot(111)

    df = {
        "fir_lpf_samples" : []
        , "fir_lpf_windowed_samples" : []
        , "samples": []
    }

    with open(f"filter_samples.csv", 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            for key in df.keys():
                df[key].append(float(row[key]))

    ax.plot(df["samples"], df["fir_lpf_samples"], color="blue", label="fir lpf")
    ax.plot(df["samples"], df["fir_lpf_windowed_samples"], color="red", label="fir lpf windowed")

    ax.set_title(f"filter samples", fontsize=20)
    ax.set_xlabel("samples", fontsize=18)
    ax.set_ylabel("filter samples", fontsize=18)
    ax.legend(fontsize=15)
    ax.grid()

    fig.savefig("filter.png")
