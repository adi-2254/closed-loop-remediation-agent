#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// A compute-heavy string search algorithm
#include <string.h>
#include <vector>
#include <algorithm>

void preprocess_bad_character(const char *pattern, int pattern_length, std::vector<int> &bad_char)
{
    const int ALPHABET_SIZE = 256; // Assuming ASCII
    bad_char.resize(ALPHABET_SIZE, -1);
    for (int i = 0; i < pattern_length; ++i)
    {
        bad_char[static_cast<unsigned char>(pattern[i])] = i;
    }
}

void preprocess_good_suffix(const char *pattern, int pattern_length, std::vector<int> &good_suffix)
{
    std::vector<int> border(pattern_length + 1, 0);
    int i = pattern_length, j = pattern_length + 1;
    border[i] = j;
    while (i > 0)
    {
        while (j <= pattern_length && pattern[i - 1] != pattern[j - 1])
        {
            if (good_suffix[j] == 0)
            {
                good_suffix[j] = j - i;
            }
            j = border[j];
        }
        --i;
        --j;
        border[i] = j;
    }
    j = border[0];
    for (i = 0; i <= pattern_length; ++i)
    {
        if (good_suffix[i] == 0)
        {
            good_suffix[i] = j;
        }
        if (i == j)
        {
            j = border[j];
        }
    }
}

int heavy_string_search(const char *text, int text_length, const char *pattern, int pattern_length)
{
    if (pattern_length == 0)
    {
        return 0;
    }

    std::vector<int> bad_char;
    std::vector<int> good_suffix(pattern_length + 1, 0);

    preprocess_bad_character(pattern, pattern_length, bad_char);
    preprocess_good_suffix(pattern, pattern_length, good_suffix);

    int count = 0;
    int s = 0; // s is the shift of the pattern with respect to text
    while (s <= (text_length - pattern_length))
    {
        int j = pattern_length - 1;

        while (j >= 0 && pattern[j] == text[s + j])
        {
            --j;
        }

        if (j < 0)
        {
            count++;
            s += good_suffix[0];
        }
        else
        {
            s += std::max(good_suffix[j + 1], j - bad_char[static_cast<unsigned char>(text[s + j])]);
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