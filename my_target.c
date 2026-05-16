#include <stdio.h>

void fast_function() {
    volatile int a = 0;
    for(int i = 0; i < 1000; i++) { a++; }
}

void slow_function() {
    volatile int b = 0;
    // Notice this loops 100 million times
    for(int i = 0; i < 100000000; i++) { b++; }
}

int main() {
    printf("Running test...\n");
    for(int i = 0; i < 10; i++) {
        fast_function();
        slow_function();
    }
    printf("Done!\n");
    return 0;
}