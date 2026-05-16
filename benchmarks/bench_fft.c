/*
 * MiBench Benchmark: Discrete Fourier Transform (Telecomm category)
 * Algorithm: Naive O(n^2) DFT (not FFT — intentionally slow)
 * Bottleneck function: compute_dft
 * Represents the MiBench telecomm/FFT workload with a naive implementation.
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846
#define N  4096  /* DFT size — large enough for meaningful profiling */

static double real_in[N];
static double imag_in[N];
static double real_out[N];
static double imag_out[N];

/* Naive O(n^2) DFT — the identified bottleneck */
void compute_dft(int n) {
    for (int k = 0; k < n; k++) {
        double sum_re = 0.0, sum_im = 0.0;
        for (int t = 0; t < n; t++) {
            double angle = 2.0 * PI * k * t / n;
            double cos_a = cos(angle);
            double sin_a = sin(angle);
            sum_re += real_in[t] * cos_a + imag_in[t] * sin_a;
            sum_im += imag_in[t] * cos_a - real_in[t] * sin_a;
        }
        real_out[k] = sum_re;
        imag_out[k] = sum_im;
    }
}

int main() {
    /* Generate a simple signal: sum of two sinusoids */
    for (int t = 0; t < N; t++) {
        real_in[t] = sin(2.0 * PI * 5  * t / N)   /* 5 Hz component */
                   + sin(2.0 * PI * 50 * t / N);  /* 50 Hz component */
        imag_in[t] = 0.0;
    }

    printf("[bench_fft] Computing naive DFT of %d points...\n", N);
    compute_dft(N);

    /* Find the peak magnitude */
    double peak = 0.0;
    int peak_k = 0;
    for (int k = 0; k < N / 2; k++) {
        double mag = sqrt(real_out[k]*real_out[k] + imag_out[k]*imag_out[k]);
        if (mag > peak) { peak = mag; peak_k = k; }
    }
    printf("[bench_fft] Done. Peak magnitude=%.2f at bin k=%d\n", peak, peak_k);
    return 0;
}
