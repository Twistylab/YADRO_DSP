#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <vector>
#include <cmath>
#include <numeric>

using namespace std;


class DSPEngine {
private:
	int delay;
	double max_quant_value;
	const int min_freq;
	const int max_freq;
	const int sampling_freq;
	const double duration;
	const int quantization_grid;
	const int interpolation_size;
	const int filter_length;
	const double pi = 3.14159265358979323846;

	vector<double> generate_sin(const int rate) {
		int rate_sampling_freq = rate * sampling_freq;
		int sampling_number = duration * rate_sampling_freq;

		vector<double> sampling_signal(sampling_number);

		for (int sample = 0; sample < sampling_number; sample++) {
			sampling_signal[sample] = sin(2 * pi * sample / (double)rate_sampling_freq * (min_freq + (max_freq - min_freq) * sample / (2 * (double)sampling_number)));
		}

		return sampling_signal;
	}

	vector<int> quantization(const vector<double>& signal_samples) {
		size_t signal_samples_length = signal_samples.size();
		vector<int> quantization_samples(signal_samples_length);

		for (int sample = 0; sample < signal_samples_length; sample++) {
			quantization_samples[sample] = round(signal_samples[sample] * ((1 << (quantization_grid - 1)) - 1));
		}

		return quantization_samples;
	}

	vector<double> floating_point_interpolation(const vector<double>& signal_samples) {
		const double norm_cutoff_freq = sampling_freq / (double)(2 * interpolation_size * sampling_freq);

		vector<double> fir_lpf(filter_length);

		vector<int> filter_samples(filter_length);

		for (int sample = 0; sample < filter_length; sample++) {
			filter_samples[sample] = sample - delay;
		}

		for (int sample = 0; sample < filter_length; sample++) {
			if (filter_samples[sample] == 0) {
				fir_lpf[sample] = 2 * norm_cutoff_freq;
			}
			else {
				fir_lpf[sample] = 2 * norm_cutoff_freq * sin(2 * pi * norm_cutoff_freq * filter_samples[sample]) / (2 * pi * norm_cutoff_freq * filter_samples[sample]);
			}
		}

		vector<double> fir_lpf_windowed(filter_length);
		const double alpha = 0.54;
		const double beta = 0.46;

		for (int sample = 0; sample < filter_length; sample++) {
			fir_lpf_windowed[sample] = fir_lpf[sample] * (alpha - beta * cos(2 * pi * (filter_samples[sample] + delay) / (filter_length - 1)));
		}

		const double sum_fir_coeff = accumulate(fir_lpf_windowed.begin(), fir_lpf_windowed.end(), 0.0);

		for (int sample = 0; sample < filter_length; sample++) {
			fir_lpf_windowed[sample] *= interpolation_size / sum_fir_coeff;
		}

		ofstream output_file_filter_samples("filter_samples.csv");

		output_file_filter_samples << "fir_lpf_samples,fir_lpf_windowed_samples,samples\n";

		for (int sample = 0; sample < filter_length; sample++) {
			output_file_filter_samples << fir_lpf[sample] << "," << fir_lpf_windowed[sample] << "," << filter_samples[sample] << "\n";
		}

		output_file_filter_samples.close();

		const size_t interpolation_signal_samples_length = interpolation_size * signal_samples.size();
		vector<double> zero_padding_signal_samples(interpolation_signal_samples_length);

		for (int sample = 0; sample < interpolation_signal_samples_length; sample++) {
			if (sample % interpolation_size == 0) {
				zero_padding_signal_samples[sample] = signal_samples[(int)(sample / interpolation_size)];
			}
			else {
				zero_padding_signal_samples[sample] = 0;
			}
		}

		vector<double> interpolation_signal_samples(interpolation_signal_samples_length + delay);

		for (int signal_sample = 0; signal_sample < interpolation_signal_samples_length + delay; signal_sample++) {
			for (int fir_sample = 0; fir_sample < filter_length; fir_sample++) {
				if ((signal_sample - fir_sample) >= 0 && (signal_sample - fir_sample) < interpolation_signal_samples_length) {
					interpolation_signal_samples[signal_sample] += fir_lpf_windowed[fir_sample] * zero_padding_signal_samples[signal_sample - fir_sample];
				}
			}
		}

		return interpolation_signal_samples;
	}

	vector<long long> fixed_point_interpolation(const vector<int>& quantization_samples) {
		const double norm_cutoff_freq = sampling_freq / (double)(2 * interpolation_size * sampling_freq);

		vector<double> fir_lpf(filter_length);

		vector<int> filter_samples(filter_length);

		for (int sample = 0; sample < filter_length; sample++) {
			filter_samples[sample] = sample - delay;
		}

		for (int sample = 0; sample < filter_length; sample++) {
			if (filter_samples[sample] == 0) {
				fir_lpf[sample] = 2 * norm_cutoff_freq;
			}
			else {
				fir_lpf[sample] = 2 * norm_cutoff_freq * sin(2 * pi * norm_cutoff_freq * filter_samples[sample]) / (2 * pi * norm_cutoff_freq * filter_samples[sample]);
			}
		}

		vector<double> fir_lpf_windowed(filter_length);
		const double alpha = 0.54;
		const double beta = 0.46;

		for (int sample = 0; sample < filter_length; sample++) {
			fir_lpf_windowed[sample] = fir_lpf[sample] * (alpha - beta * cos(2 * pi * (filter_samples[sample] + delay) / (filter_length - 1)));
		}

		const double sum_fir_coeff = accumulate(fir_lpf_windowed.begin(), fir_lpf_windowed.end(), 0.0);

		for (int sample = 0; sample < filter_length; sample++) {
			fir_lpf_windowed[sample] *= interpolation_size / sum_fir_coeff;
		}

		vector<int> fixed_point_fir_lpf_windowed(filter_length);

		for (int sample = 0; sample < filter_length; sample++) {
			fixed_point_fir_lpf_windowed[sample] = round(fir_lpf_windowed[sample] * max_quant_value);
		}

		const size_t interpolation_quantization_samples_length = interpolation_size * quantization_samples.size();
		vector<int> zero_padding_quantization_samples(interpolation_quantization_samples_length);

		for (int sample = 0; sample < interpolation_quantization_samples_length; sample++) {
			if (sample % interpolation_size == 0) {
				zero_padding_quantization_samples[sample] = quantization_samples[(int)(sample / interpolation_size)];
			}
			else {
				zero_padding_quantization_samples[sample] = 0;
			}
		}

		vector<long long> interpolation_quantization_samples(interpolation_quantization_samples_length + delay);

		for (int quantization_sample = 0; quantization_sample < interpolation_quantization_samples_length + delay; quantization_sample++) {
			for (int fir_sample = 0; fir_sample < filter_length; fir_sample++) {
				if ((quantization_sample - fir_sample) >= 0 && (quantization_sample - fir_sample) < interpolation_quantization_samples_length) {
					interpolation_quantization_samples[quantization_sample] += ((long long)fixed_point_fir_lpf_windowed[fir_sample] * zero_padding_quantization_samples[quantization_sample - fir_sample]) >> (quantization_grid - 1);
				}
			}
		}

		return interpolation_quantization_samples;
	}

	vector<double> interpolation_abs_error_vs_freq(const vector<double>& ideal_interpolation_samples, const vector<double>& interpolation_samples) {
		size_t interpolation_samples_length = ideal_interpolation_samples.size();
		vector<double> abs_error(interpolation_samples_length);

		for (int sample = 0; sample < interpolation_samples_length; sample++) {
			abs_error[sample] = abs(ideal_interpolation_samples[sample] - interpolation_samples[sample + delay]);
		}

		return abs_error;
	}

	double quantization_mse(const vector<double>& ideal_signal_samples, const vector<double>& quantization_signal_samples) {
		size_t signal_samples_length = ideal_signal_samples.size();
		double mse_error = 0.0;

		for (int sample = 0; sample < signal_samples_length; sample++) {
			mse_error += pow((ideal_signal_samples[sample] - quantization_signal_samples[sample]), 2) / (double)signal_samples_length;
		}

		return mse_error;
	}

public:
	double quant_mse;
	vector<double> floating_point_interpolation_abs_error_vs_freq;
	vector<double> fixed_point_interpolation_abs_error_vs_freq;

	DSPEngine(int f_min, int f_max, int f_s, double dur, int quant_grid, int inter_size, int filter_len) :
		min_freq(f_min)
		, max_freq(f_max)
		, sampling_freq(f_s)
		, duration(dur)
		, quantization_grid(quant_grid)
		, interpolation_size(inter_size)
		, filter_length(filter_len) {

		delay = (int)((filter_length - 1) / 2.0f);

		max_quant_value = (1 << (quantization_grid - 1)) - 1;

		vector<double> signal_samples = generate_sin(1);

		const size_t signal_samples_length = signal_samples.size();


		vector<int> quantization_samples = quantization(signal_samples);


		vector<double> quantization_signal_samples(signal_samples_length);

		for (int sample = 0; sample < signal_samples_length; sample++) {
			quantization_signal_samples[sample] = quantization_samples[sample] / max_quant_value;
		}

		ofstream output_file_signal_and_quantization_samples("signal_and_quantization_samples.csv");

		output_file_signal_and_quantization_samples << "signal_samples,quantization_samples,time_samples\n";

		for (int sample = 0; sample < signal_samples_length; sample++) {
			double time_sample = sample / (sampling_freq * duration);
			output_file_signal_and_quantization_samples << signal_samples[sample] << "," << quantization_signal_samples[sample] << "," << time_sample << "\n";
		}

		output_file_signal_and_quantization_samples.close();

		quant_mse = quantization_mse(signal_samples, quantization_signal_samples);

		vector<double> floating_point_interpolation_signal_samples = floating_point_interpolation(quantization_signal_samples);

		vector<long long> interpolation_quantization_samples = fixed_point_interpolation(quantization_samples);

		vector<double> fixed_point_interpolation_signal_samples(interpolation_size * signal_samples_length + delay);

		for (int sample = 0; sample < interpolation_size * signal_samples_length + delay; sample++) {
			fixed_point_interpolation_signal_samples[sample] = interpolation_quantization_samples[sample] / max_quant_value;
		}

		vector<double> ideal_interpolation_signal_samples = generate_sin(interpolation_size);

		ofstream output_file_interpolation_signal_samples("interpolation_signal_samples.csv");

		output_file_interpolation_signal_samples << "floating_point_interpolation_signal_samples,fixed_point_interpolation_signal_samples,ideal_interpolation_signal_samples,time_samples\n";

		for (int sample = 0; sample < interpolation_size * signal_samples_length; sample++) {
			double time_sample = sample / (interpolation_size * sampling_freq * duration);
			output_file_interpolation_signal_samples << floating_point_interpolation_signal_samples[sample + delay] << "," << fixed_point_interpolation_signal_samples[sample + delay] << "," << ideal_interpolation_signal_samples[sample] << "," << time_sample << "\n";
		}

		output_file_interpolation_signal_samples.close();

		floating_point_interpolation_abs_error_vs_freq = interpolation_abs_error_vs_freq(ideal_interpolation_signal_samples, floating_point_interpolation_signal_samples);
		fixed_point_interpolation_abs_error_vs_freq = interpolation_abs_error_vs_freq(ideal_interpolation_signal_samples, fixed_point_interpolation_signal_samples);
	}
};


int main() {
	const int min_freq = 0, max_freq = 50, sampling_freq = 100;
	const double duration = 1.0;
	const int quantization_grid = 16;
	const int interpolation_size = 2;
	const int filter_length = 31;

	DSPEngine dsp_example(min_freq, max_freq, sampling_freq, duration, quantization_grid, interpolation_size, filter_length);

	double mse = dsp_example.quant_mse;

	ofstream output_file_mse("quantization_mse.json");

	output_file_mse << "{\n";

	output_file_mse << "  \"" << "quantization_mse" << "\": " << mse << "\n";

	output_file_mse << "}\n";

	output_file_mse.close();

	vector<double> floating_point_error = dsp_example.floating_point_interpolation_abs_error_vs_freq;
	vector<double> fixed_point_error = dsp_example.fixed_point_interpolation_abs_error_vs_freq;

	ofstream output_file_abs("interpolation_abs_error_vs_frequency.csv");

	output_file_abs << "floating_point_interpolation_abs_error,fixed_point_interpolation_abs_error,frequency\n";

	for (int sample = 0; sample < fixed_point_error.size(); sample++) {
		double freq_n = min_freq + (max_freq - min_freq) * sample / (interpolation_size * sampling_freq * duration);
		output_file_abs << floating_point_error[sample] << "," << fixed_point_error[sample] << "," << freq_n << "\n";
	}

	output_file_abs.close();

	return 0;
}