/*
 * MiBench Benchmark: String Search (Automotive category)
 * Algorithm: Naive O(n*m) brute-force string search
 * Bottleneck function: heavy_string_search
 * This mimics the MiBench basicmath/string search workload.
 */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/* Deliberately naive O(n*m) search — the identified bottleneck */
int heavy_string_search(const char *text, int text_length,
                        const char *pattern, int pattern_length) {
    int count = 0;
    for (int i = 0; i <= text_length - pattern_length; i++) {
        int j;
        for (j = 0; j < pattern_length; j++) {
            if (text[i + j] != pattern[j]) break;
        }
        if (j == pattern_length) count++;
    }
    return count;
}

int main() {
    const int text_len = 20000000; /* 20M characters */
    char *big_text = (char *)malloc(text_len + 1);
    if (!big_text) { fprintf(stderr, "malloc failed\n"); return 1; }

    for (int i = 0; i < text_len; i++)
        big_text[i] = "ABCDE"[i % 5];
    big_text[text_len] = '\0';

    const char *pattern = "ABCDE";
    int pat_len = (int)strlen(pattern);

    printf("[bench_string_search] Starting naive string search...\n");
    int hits = heavy_string_search(big_text, text_len, pattern, pat_len);
    printf("[bench_string_search] Found %d occurrences.\n", hits);

    free(big_text);
    return 0;
}
