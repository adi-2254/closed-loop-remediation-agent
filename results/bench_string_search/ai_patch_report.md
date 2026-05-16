```c
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
```