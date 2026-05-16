```c
#include <math.h>

void compute_dct(double matrix[N][N], double dct[N][N])
{
    static const double c0 = 1.0 / sqrt(2.0);
    double cos_table[N][N];
    double cu, cv, sum;
    int i, j, u, v;

    for (i = 0; i < N; ++i)
        for (j = 0; j < N; ++j)
            cos_table[i][j] = cos((2.0 * i + 1.0) * j * M_PI / (2.0 * N));

    for (u = 0; u < N; ++u)
    {
        cu = (u == 0) ? c0 : 1.0;
        for (v = 0; v < N; ++v)
        {
            cv = (v == 0) ? c0 : 1.0;
            sum = 0.0;
            for (i = 0; i < N; ++i)
                for (j = 0; j < N; ++j)
                    sum += matrix[i][j] * cos_table[i][u] * cos_table[j][v];
            dct[u][v] = 0.25 * cu * cv * sum;
        }
    }
}
```