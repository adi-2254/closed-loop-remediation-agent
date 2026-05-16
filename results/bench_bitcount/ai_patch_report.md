The original `count_bits` function counts the number of set bits (1s) in a 32-bit unsigned integer using a simple loop that checks each bit individually. This approach can be optimized using a more efficient algorithm known as "Brian Kernighan's Algorithm," which iteratively clears the least significant set bit until the number becomes zero. This method reduces the number of iterations to the number of set bits, which is generally much smaller than 32.

Here's the optimized version of the `count_bits` function using Brian Kernighan's Algorithm:

```c
int count_bits(uint32_t value) {
    int count = 0;
    while (value) {
        value &= (value - 1); // Clear the least significant bit set
        count++;
    }
    return count;
}
```

### Explanation:
- **Original Approach**: The original function shifts the bits of the number one by one and checks each bit. This results in up to 32 iterations for a 32-bit integer.
- **Optimized Approach**: Brian Kernighan's Algorithm reduces the number of iterations to the number of set bits. Each iteration clears the least significant set bit, which is done using the expression `value &= (value - 1)`. This operation effectively removes the lowest set bit in the number, and the loop continues until all bits are cleared.

This optimized version is more efficient, especially when the input number has a small number of set bits.