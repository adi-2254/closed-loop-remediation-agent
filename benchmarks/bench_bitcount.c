/*
 * MiBench Benchmark: Bit Counting (Automotive / Integer category)
 * Algorithm: Naive bit counting via shift-and-mask loop
 * Bottleneck function: count_bits
 * Represents MiBench bitcount workload with naive popcount.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

/* Naive bit counter — 32 iterations per value — the identified bottleneck */
int count_bits(uint32_t value) {
    int count = 0;
    while (value) {
        count += (int)(value & 1u);
        value >>= 1;
    }
    return count;
}

/* Process a large array of values */
long long count_bits_array(const uint32_t *arr, int n) {
    long long total = 0;
    for (int i = 0; i < n; i++)
        total += count_bits(arr[i]);
    return total;
}

int main() {
    const int SIZE = 10000000; /* 10M values */
    uint32_t *data = (uint32_t *)malloc(SIZE * sizeof(uint32_t));
    if (!data) { fprintf(stderr, "malloc failed\n"); return 1; }

    /* Fill with varied data */
    for (int i = 0; i < SIZE; i++)
        data[i] = (uint32_t)(i * 2654435761u); /* Knuth multiplicative hash */

    printf("[bench_bitcount] Counting bits in %d uint32 values...\n", SIZE);
    long long total = count_bits_array(data, SIZE);
    printf("[bench_bitcount] Total set bits = %lld\n", total);

    free(data);
    return 0;
}
