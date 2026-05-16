/*
 * MiBench Benchmark: SHA Compression (Security category)
 * Algorithm: Simplified SHA-1-style message schedule + compression
 * Bottleneck function: sha_compress
 * Represents the MiBench security/sha workload.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define ROTL32(v, n) (((v) << (n)) | ((v) >> (32 - (n))))

/* SHA-1-style constants */
static const uint32_t K[4] = {
    0x5A827999u, 0x6ED9EBA1u, 0x8F1BBCDCu, 0xCA62C1D6u
};

/* Simplified SHA-1 compression round — the identified bottleneck */
#include <stdint.h>

#define ROTL32(x, n) (((x) << (n)) | ((x) >> (32 - (n))))

void sha_compress(uint32_t *state, const uint32_t *block, int rounds) {
    uint32_t W[80];
    uint32_t a, b, c, d, e, f, T;
    const uint32_t K[4] = {0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xCA62C1D6};

    for (int blk = 0; blk < rounds; blk++) {
        /* Message schedule */
        for (int t = 0; t < 16; t++) {
            W[t] = block[t] ^ (uint32_t)blk;  /* Vary per round */
        }
        for (int t = 16; t < 80; t++) {
            W[t] = ROTL32(W[t-3] ^ W[t-8] ^ W[t-14] ^ W[t-16], 1);
        }

        a = state[0]; b = state[1]; c = state[2];
        d = state[3]; e = state[4];

        /* Unroll the loop in chunks of 20 */
        for (int t = 0; t < 80; t += 20) {
            uint32_t Kt = K[t/20];

            for (int i = 0; i < 20; i++) {
                if (t + i < 20)
                    f = (b & c) | ((~b) & d);
                else if (t + i < 40)
                    f = b ^ c ^ d;
                else if (t + i < 60)
                    f = (b & c) | (b & d) | (c & d);
                else
                    f = b ^ c ^ d;

                T = ROTL32(a, 5) + f + e + Kt + W[t + i];
                e = d; d = c;
                c = ROTL32(b, 30);
                b = a; a = T;
            }
        }

        state[0] += a; state[1] += b; state[2] += c;
        state[3] += d; state[4] += e;
    }
}


int main() {
    uint32_t state[5] = {
        0x67452301u, 0xEFCDAB89u, 0x98BADCFEu,
        0x10325476u, 0xC3D2E1F0u
    };
    uint32_t block[16];
    for (int i = 0; i < 16; i++)
        block[i] = (uint32_t)(i * 0xDEADBEEFu);

    const int ROUNDS = 50000;
    printf("[bench_sha] Running %d SHA-1 compression rounds...\n", ROUNDS);
    sha_compress(state, block, ROUNDS);
    printf("[bench_sha] Done. Hash[0]=0x%08X Hash[4]=0x%08X\n",
           state[0], state[4]);
    return 0;
}
