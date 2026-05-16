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
#include <string.h>

int heavy_string_search(const char *text, int text_length, const char *pattern, int pattern_length)
{
    if (pattern_length == 0 || text_length < pattern_length)
        return 0;

    int count = 0;
    int *bad_char_skip = (int *)malloc(256 * sizeof(int));
    for (int i = 0; i < 256; i++)
        bad_char_skip[i] = pattern_length;

    for (int i = 0; i < pattern_length - 1; i++)
        bad_char_skip[(unsigned char)pattern[i]] = pattern_length - i - 1;

    int i = 0;
    while (i <= text_length - pattern_length) {
        int j = pattern_length - 1;
        while (j >= 0 && pattern[j] == text[i + j])
            j--;

        if (j < 0) {
            count++;
            i += bad_char_skip[(unsigned char)text[i + pattern_length]];
        } else {
            i += bad_char_skip[(unsigned char)text[i + j]];
        }
    }

    free(bad_char_skip);
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
