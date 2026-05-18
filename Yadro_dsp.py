import csv
import subprocess
import matplotlib.pyplot as plt

if __name__ == "__main__":
    subprocess.run(["./dsp.exe"], check=True)

    fig = plt.figure(figsize=(16, 16))
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
    ax.legend(fontsize=15)
    ax.grid()

    fig.savefig("abs_error_vs_freq.png")
