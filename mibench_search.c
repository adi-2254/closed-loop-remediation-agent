#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// A compute-heavy string search algorithm
int heavy_string_search(const char *text, int text_length, const char *pattern, int pattern_length) {
    int count = 0;
    for (int i = 0; i <= text_length - pattern_length; i++) {
        int j;
        for (j = 0; j < pattern_length; j++) {
            if (text[i + j] != pattern[j]) {
                break;
            }
        }
        if (j == pattern_length) {
            count++;
        }
    }
    return count;
}

int main() {
    int text_len = 50000000; // 50 million characters
    char *big_text = (char *)malloc(text_len + 1);
    
    // Fill the memory with a repeating pattern
    for (int i = 0; i < text_len; i++) {
        big_text[i] = (i % 2 == 0) ? 'A' : 'B';
    }
    big_text[text_len] = '\0';

    const char *pattern = "ABABA";
    int pat_len = strlen(pattern);

    printf("Starting heavy string search stress test...\n");
    int occurrences = heavy_string_search(big_text, text_len, pattern, pat_len);
    
    printf("Found %d occurrences.\n", occurrences);
    free(big_text);
    return 0;
}