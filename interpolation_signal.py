import csv
import subprocess
import matplotlib.pyplot as plt

if __name__ == "__main__":
    subprocess.run(["./dsp.exe"], check=True)

    fig = plt.figure(figsize=(30, 30))
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
    ax.legend(fontsize=15)
    ax.grid()

    ax2 = fig.add_subplot(212)

    ax2.plot(df_interpolation["time_samples"], df_interpolation["fixed_point_interpolation_signal_samples"], color="blue", label="fixed point interpolation signal samples")
    ax2.plot(df_interpolation["time_samples"], df_interpolation["ideal_interpolation_signal_samples"], color="red", label="ideal interpolation signal samples")
    ax2.plot(df["time_samples"], df["signal_samples"], color="green", label="signal samples")

    ax2.set_title(f"ideal and fixed point interpolation signal samples\n mean absolute error interpolation {round(sum(df_error["fixed_point_interpolation_abs_error"]) / len(df_error["fixed_point_interpolation_abs_error"]) * 1e3, 2)}" + r"$\cdot 10^{-3}$", fontsize=20)
    ax2.set_xlabel("time, s", fontsize=18)
    ax2.set_ylabel("samples", fontsize=18)
    ax2.legend(fontsize=15)
    ax2.grid()

    fig.savefig("ideal_and_interpolation_signal.png")
