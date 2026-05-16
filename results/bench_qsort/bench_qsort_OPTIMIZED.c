/*
 * MiBench Benchmark: Sorting (Automotive category)
 * Algorithm: Bubble Sort on a large random array
 * Bottleneck function: bubble_sort
 * This mimics the MiBench qsort workload but using a naive sort
 * so the PIN tool can clearly identify it as the bottleneck.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define ARRAY_SIZE 80000

/* Deliberately O(n^2) bubble sort — the identified bottleneck */
void bubble_sort(int *arr, int n)
{
  int newn;
  do {
    newn = 0;
    for (int i = 1; i < n; i++) {
      if (arr[i - 1] > arr[i]) {
        int tmp = arr[i - 1];
        arr[i - 1] = arr[i];
        arr[i] = tmp;
        newn = i;
      }
    }
    n = newn;
  } while (newn > 0);
}


/* Seeded LCG for reproducible random data */
static unsigned int lcg_rand(unsigned int *state) {
    *state = (*state * 1664525u) + 1013904223u;
    return *state;
}

int main() {
    int *arr = (int *)malloc(ARRAY_SIZE * sizeof(int));
    if (!arr) { fprintf(stderr, "malloc failed\n"); return 1; }

    unsigned int seed = 42;
    for (int i = 0; i < ARRAY_SIZE; i++)
        arr[i] = (int)(lcg_rand(&seed) % 1000000);

    printf("[bench_qsort] Bubble sorting %d integers...\n", ARRAY_SIZE);
    bubble_sort(arr, ARRAY_SIZE);
    printf("[bench_qsort] Done. First=%-8d Last=%d\n", arr[0], arr[ARRAY_SIZE - 1]);

    free(arr);
    return 0;
}
