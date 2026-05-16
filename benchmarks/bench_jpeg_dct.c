#include <stdio.h>
#include <math.h>
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define N 8

void compute_dct(double matrix[N][N], double dct[N][N]) {
    int i, j, u, v;
    double cu, cv, sum;
    for (u = 0; u < N; ++u) {
        for (v = 0; v < N; ++v) {
            if (u == 0) cu = 1.0 / sqrt(2.0); else cu = 1.0;
            if (v == 0) cv = 1.0 / sqrt(2.0); else cv = 1.0;
            sum = 0.0;
            for (i = 0; i < N; ++i) {
                for (j = 0; j < N; ++j) {
                    sum += matrix[i][j] * cos((2.0 * i + 1.0) * u * M_PI / 16.0) * cos((2.0 * j + 1.0) * v * M_PI / 16.0);
                }
            }
            dct[u][v] = 0.25 * cu * cv * sum;
        }
    }
}

int main() {
    double matrix[N][N];
    double dct[N][N];
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            matrix[i][j] = (i + j) % 255;
        }
    }
    for (int k = 0; k < 100000; k++) {
        compute_dct(matrix, dct);
    }
    printf("DCT benchmark complete. Checksum: %f\n", dct[0][0]);
    return 0;
}