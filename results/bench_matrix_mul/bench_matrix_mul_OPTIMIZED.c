/*
 * MiBench Benchmark: Matrix Multiplication (Telecomm / Network category)
 * Algorithm: Naive O(n^3) matrix multiply
 * Bottleneck function: matrix_multiply
 * Represents dense linear algebra compute kernels in MiBench.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N 300  /* 300x300 matrices — large enough for PIN to profile */

static double A[N][N];
static double B[N][N];
static double C[N][N];

/* Naive O(n^3) matrix multiplication — the identified bottleneck */
void matrix_multiply(int n)
{
  for (int i = 0; i < n; i++)
  {
    for (int k = 0; k < n; k++)
    {
      double temp = A[i][k];
      for (int j = 0; j < n; j++)
      {
        C[i][j] += temp * B[k][j];
      }
    }
  }
}


int main() {
    /* Initialize with simple patterns */
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) {
            A[i][j] = (double)(i + j + 1);
            B[i][j] = (double)(i - j + N);
        }

    printf("[bench_matrix_mul] Multiplying %dx%d matrices (naive O(n^3))...\n", N, N);
    matrix_multiply(N);
    printf("[bench_matrix_mul] Done. C[0][0]=%.2f  C[%d][%d]=%.2f\n",
           C[0][0], N-1, N-1, C[N-1][N-1]);
    return 0;
}
