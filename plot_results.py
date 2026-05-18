import csv
import json
import subprocess
import matplotlib.pyplot as plt


def plot_interpolation_abs_error_vs_frequency():
    fig = plt.figure(figsize=(16, 10))
    ax = fig.add_subplot(111)

    df = {
        "floating_point_interpolation_abs_error" : []
        , "fixed_point_interpolation_abs_error" : []
        , "frequency": []
    }

    with open(f"interpolation_abs_error_vs_frequency.csv", 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            floating_point_error = float(row["floating_point_interpolation_abs_error"])
            fixed_point_error = float(row["fixed_point_interpolation_abs_error"])
            freq = float(row["frequency"])

            df["floating_point_interpolation_abs_error"].append(floating_point_error)
            df["fixed_point_interpolation_abs_error"].append(fixed_point_error)
            df["frequency"].append(freq)  

    ax.semilogy(df["frequency"], df["floating_point_interpolation_abs_error"], color="blue", label="floating point interpolation")
    ax.semilogy(df["frequency"], df["fixed_point_interpolation_abs_error"], color="red", label="fixed point interpolation")

    ax.set_title("Absolute error of floating and fixed point interpolation", fontsize=20)
    ax.set_xlabel("frequency, Hz", fontsize=18)
    ax.set_ylabel("absolute error", fontsize=18)
    ax.legend(loc='upper left', fontsize=15)
    ax.grid()

    fig.savefig("abs_error_vs_freq.png")


def plot_signal_and_quantization_samples():
    with open("quantization_mse.json", 'r') as file:
        data = json.load(file)

    mse = data["quantization_mse"]

    fig = plt.figure(figsize=(16, 10))
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
    ax.legend(loc='upper left', fontsize=15)
    ax.grid()

    fig.savefig("signal_and_quantization.png")

def plot_ideal_and_interpolation_signal():
    fig = plt.figure(figsize=(16, 20))
    ax = fig.add_subplot(211)

    df_error = {
        "floating_point_interpolation_abs_error" : []
        , "fixed_point_interpolation_abs_error" : []
        , "frequency": []
    }

    with open(f"interpolation_abs_error_vs_frequency.csv", 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            for key in df_error.keys():
                df_error[key].append(float(row[key]))

    df_interpolation = {
        "floating_point_interpolation_signal_samples" : []
        , "fixed_point_interpolation_signal_samples" : []
        , "ideal_interpolation_signal_samples" : []
        , "time_samples": []
    }

    with open(f"interpolation_signal_samples.csv", 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            for key in df_interpolation.keys():
                df_interpolation[key].append(float(row[key]))

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

    ax.plot(df_interpolation["time_samples"], df_interpolation["floating_point_interpolation_signal_samples"], color="blue", label="floating point interpolation signal samples")
    ax.plot(df_interpolation["time_samples"], df_interpolation["ideal_interpolation_signal_samples"], color="red", label="ideal interpolation signal samples")
    ax.plot(df["time_samples"], df["signal_samples"], color="green", label="signal samples")

    ax.set_title(f"ideal and floating point interpolation signal samples\n mean absolute error interpolation {round(sum(df_error["floating_point_interpolation_abs_error"]) / len(df_error["floating_point_interpolation_abs_error"]) * 1e3, 2)}" + r"$\cdot 10^{-3}$", fontsize=20)
    ax.set_xlabel("time, s", fontsize=18)
    ax.set_ylabel("samples", fontsize=18)
    ax.legend(loc='upper left', fontsize=15)
    ax.grid()

    ax2 = fig.add_subplot(212)

    ax2.plot(df_interpolation["time_samples"], df_interpolation["fixed_point_interpolation_signal_samples"], color="blue", label="fixed point interpolation signal samples")
    ax2.plot(df_interpolation["time_samples"], df_interpolation["ideal_interpolation_signal_samples"], color="red", label="ideal interpolation signal samples")
    ax2.plot(df["time_samples"], df["signal_samples"], color="green", label="signal samples")

    ax2.set_title(f"ideal and fixed point interpolation signal samples\n mean absolute error interpolation {round(sum(df_error["fixed_point_interpolation_abs_error"]) / len(df_error["fixed_point_interpolation_abs_error"]) * 1e3, 2)}" + r"$\cdot 10^{-3}$", fontsize=20)
    ax2.set_xlabel("time, s", fontsize=18)
    ax2.set_ylabel("samples", fontsize=18)
    ax2.legend(loc='upper left', fontsize=15)
    ax2.grid()

    fig.savefig("ideal_and_interpolation_signal.png")

def plot_filter():
    fig = plt.figure(figsize=(16, 10))
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
    ax.legend(loc='upper left', fontsize=15)
    ax.grid()

    fig.savefig("filter.png")


if __name__ == "__main__":
    subprocess.run(["./dsp.exe"], check=True)

    plot_interpolation_abs_error_vs_frequency()
    plot_signal_and_quantization_samples()
    plot_ideal_and_interpolation_signal()
    plot_filter()
