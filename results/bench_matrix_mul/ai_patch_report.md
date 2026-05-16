```c
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
```