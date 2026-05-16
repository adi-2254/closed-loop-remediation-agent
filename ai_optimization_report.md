# AI Automated Optimization Report

### Optimization Report for `heavy_string_search`

#### 1. Algorithmic Diagnosis

The provided function implements a naive string search algorithm, which has a time complexity of O(n * m), where `n` is the length of the text and `m` is the length of the pattern. This approach is inefficient for large texts and patterns due to the following reasons:

- **Redundant Comparisons**: The naive algorithm checks each position in the text even if it is clear from previous checks that a match is impossible.
- **Lack of Preprocessing**: The algorithm does not preprocess the pattern to skip unnecessary comparisons, which is a key feature of more advanced algorithms like Knuth-Morris-Pratt (KMP) or Boyer-Moore (BM).
- **Branch Mis-predictions**: The inner loop contains a conditional branch that can lead to frequent mis-predictions, especially if the pattern is not found often.

#### 2. Code-Level Optimizations

To optimize the function, we can implement the Boyer-Moore algorithm, which is generally faster for typical text search tasks due to its ability to skip sections of the text. Additionally, we can consider using SIMD instructions for further optimization, but let's first focus on the algorithmic improvement.

Here is an optimized version using the Boyer-Moore algorithm:

```c
#include <string.h>
#include <vector>

int heavy_string_search(const char *text, int text_length, const char *pattern, int pattern_length)
{
    if (pattern_length == 0 || text_length < pattern_length) {
        return 0;
    }

    // Preprocessing: Bad character heuristic
    std::vector<int> bad_char(256, -1);
    for (int i = 0; i < pattern_length; i++) {
        bad_char[(unsigned char)pattern[i]] = i;
    }

    int count = 0;
    int shift = 0;

    while (shift <= (text_length - pattern_length)) {
        int j = pattern_length - 1;

        // Compare pattern from the end
        while (j >= 0 && pattern[j] == text[shift + j]) {
            j--;
        }

        // If the pattern is present at the current shift
        if (j < 0) {
            count++;
            // Shift the pattern so that the next character in text aligns with the last occurrence of it in pattern
            shift += (shift + pattern_length < text_length) ? pattern_length - bad_char[(unsigned char)text[shift + pattern_length]] : 1;
        } else {
            // Shift the pattern so that the bad character in text aligns with the last occurrence of it in pattern
            shift += std::max(1, j - bad_char[(unsigned char)text[shift + j]]);
        }
    }

    return count;
}
```

### Explanation of Optimizations

- **Boyer-Moore Algorithm**: This algorithm uses two heuristics, the bad character heuristic and the good suffix heuristic, to skip sections of the text, reducing the number of comparisons.
- **Bad Character Heuristic**: We preprocess the pattern to create a table (`bad_char`) that tells us how far to shift the pattern when a mismatch occurs.
- **Efficient Shifting**: By using the precomputed table, we can skip over sections of the text that cannot possibly match the pattern, leading to significant performance improvements over the naive approach.

### Further Optimizations

- **SIMD Instructions**: For even further optimization, especially on large datasets, consider using SIMD instructions to compare multiple characters at once. This requires careful handling of alignment and boundary conditions.
- **Parallelization**: If the text is very large, consider parallelizing the search across multiple threads, especially if the text can be divided into independent sections.

By implementing the Boyer-Moore algorithm, we significantly reduce the number of character comparisons, leading to faster execution times, especially for longer texts and patterns.