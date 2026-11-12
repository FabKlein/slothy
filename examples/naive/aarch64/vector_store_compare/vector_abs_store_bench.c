#define _GNU_SOURCE
#include "vector_abs_store_kernels.h"

#include <errno.h>
#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef void (*kernel)(uint32_t *, const uint32_t *, size_t);

static uint64_t now_ns(void)
{
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC_RAW, &ts)) {
        perror("clock_gettime");
        exit(EXIT_FAILURE);
    }
    return (uint64_t)ts.tv_sec * UINT64_C(1000000000) + (uint64_t)ts.tv_nsec;
}

static void barrier(void)
{
    __asm__ volatile("dsb ish\n\tisb" ::: "memory");
}

static double measure(kernel fn, uint32_t *dst, const uint32_t *src,
                      size_t blocks, size_t repetitions)
{
    for (unsigned i = 0; i < 16; ++i)
        fn(dst, src, blocks);
    barrier();
    uint64_t start = now_ns();
    for (size_t i = 0; i < repetitions; ++i)
        fn(dst, src, blocks);
    barrier();
    return (double)(now_ns() - start) / (double)repetitions;
}

static size_t positive_size(const char *text)
{
    char *end;
    errno = 0;
    unsigned long long value = strtoull(text, &end, 10);
    if (errno || *text < '0' || *text > '9' || *end || !value || value > SIZE_MAX) {
        fprintf(stderr, "Invalid positive integer: %s\n", text);
        exit(EXIT_FAILURE);
    }
    return (size_t)value;
}

static int compare_double(const void *a, const void *b)
{
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

static double median(double *values, size_t n)
{
    qsort(values, n, sizeof(*values), compare_double);
    return n % 2 ? values[n / 2] : (values[n / 2 - 1] + values[n / 2]) / 2;
}

static void report(const char *name, double *values, size_t n, size_t blocks,
                   double mhz)
{
    double avg = 0;
    for (size_t i = 0; i < n; ++i)
        avg += values[i] / (double)n;
    double med = median(values, n);
    printf("%s ns/call: min %.2f  avg %.2f  median %.2f  max %.2f\n",
           name, values[0], avg, med, values[n - 1]);
    printf("    median %.3f ns / 64 floats", med / (double)blocks);
    if (mhz > 0)
        printf("; %.3f estimated cycles / 64 floats", med * mhz / 1000 / blocks);
    putchar('\n');
}

static int check(const uint32_t *dst, const uint32_t *src, size_t words,
                 const unsigned char *src_raw, const unsigned char *dst_raw)
{
    for (size_t i = 0; i < words; ++i) {
        if (dst[i] != (src[i] & UINT32_C(0x7fffffff))) {
            fprintf(stderr, "Mismatch at word %zu: %08" PRIx32 "\n", i, dst[i]);
            return 0;
        }
    }
    size_t bytes = words * sizeof(*src);
    for (size_t i = 0; i < 64; ++i) {
        if (src_raw[4096 - 64 + i] != 0xa5 || src_raw[4096 + bytes + i] != 0xa5 ||
            dst_raw[4096 - 64 + i] != 0xa5 || dst_raw[4096 + bytes + i] != 0xa5) {
            fprintf(stderr, "Buffer guard corrupted\n");
            return 0;
        }
    }
    return 1;
}

int main(int argc, char **argv)
{
    if (argc > 5 || (argc > 1 && !strcmp(argv[1], "--help"))) {
        fprintf(stderr, "Usage: %s [blocks=32] [repetitions=1000] [samples=21] "
                        "[clock_mhz=0]\nOne block = 64 floats (256 bytes); blocks >= 2.\n",
                argv[0]);
        return argc > 5 ? EXIT_FAILURE : EXIT_SUCCESS;
    }
    size_t blocks = argc > 1 ? positive_size(argv[1]) : 32;
    size_t repetitions = argc > 2 ? positive_size(argv[2]) : 1000;
    size_t samples = argc > 3 ? positive_size(argv[3]) : 21;
    double mhz = 0;
    if (argc > 4) {
        char *end;
        errno = 0;
        mhz = strtod(argv[4], &end);
        if (errno || !*argv[4] || *end || !isfinite(mhz) || mhz < 0) {
            fprintf(stderr, "clock_mhz must be finite and nonnegative\n");
            return EXIT_FAILURE;
        }
    }
    if (blocks < 2 || blocks > (SIZE_MAX - 8192) / 256 ||
        samples > SIZE_MAX / sizeof(double)) {
        fprintf(stderr, "Invalid block count or allocation size\n");
        return EXIT_FAILURE;
    }
    size_t bytes = blocks * 256, words = blocks * 64;
    unsigned char *src_raw = NULL, *dst_raw = NULL;
    double *times[2] = {calloc(samples, sizeof(double)), calloc(samples, sizeof(double))};
    double *ratios = calloc(samples, sizeof(double));
    if (posix_memalign((void **)&src_raw, 4096, bytes + 8192) ||
        posix_memalign((void **)&dst_raw, 4096, bytes + 8192) ||
        !times[0] || !times[1] || !ratios) {
        fprintf(stderr, "Allocation failed\n");
        free(src_raw);
        free(dst_raw);
        free(times[0]);
        free(times[1]);
        free(ratios);
        return EXIT_FAILURE;
    }
    memset(src_raw, 0xa5, bytes + 8192);
    memset(dst_raw, 0xa5, bytes + 8192);
    uint32_t *src = (uint32_t *)(src_raw + 4096);
    uint32_t *dst = (uint32_t *)(dst_raw + 4096);
    const uint32_t edges[] = {0, 0x80000000, 0x3f800000, 0xbf800000,
                             0x7f800000, 0xff800000, 0xffc12345, 0x80000001};
    uint32_t state = UINT32_C(0x31415926);
    for (size_t i = 0; i < words; ++i) {
        state = state * UINT32_C(1664525) + UINT32_C(1013904223);
        src[i] = i < sizeof(edges) / sizeof(*edges) ? edges[i] : state;
    }
    kernel functions[] = {vector_abs_st1, vector_abs_str};
    const char *names[] = {"ST1", "STR"};
    int ok = 1;
    for (unsigned k = 0; k < 2; ++k) {
        memset(dst, 0x5a, bytes);
        functions[k](dst, src, blocks);
        ok &= check(dst, src, words, src_raw, dst_raw);
    }
    if (ok) {
        printf("%zu blocks, %zu floats, %zu bytes/buffer; %zu repetitions x %zu pairs\n",
               blocks, words, bytes, repetitions, samples);
        puts("CLOCK_MONOTONIC_RAW; warm buffers; alternating ST1/STR and STR/ST1 order.");
        for (size_t s = 0; s < samples && ok; ++s) {
            for (unsigned order = 0; order < 2; ++order) {
                unsigned k = (s + order) % 2;
                times[k][s] = measure(functions[k], dst, src, blocks, repetitions);
                ok &= check(dst, src, words, src_raw, dst_raw);
            }
            if (times[0][s] <= 0 || times[1][s] <= 0) {
                fprintf(stderr, "Timing batch too short; increase repetitions\n");
                ok = 0;
            } else {
                ratios[s] = times[0][s] / times[1][s];
            }
        }
        if (ok) {
            for (unsigned k = 0; k < 2; ++k)
                report(names[k], times[k], samples, blocks, mhz);
            printf("Paired median ST1/STR time ratio: %.4f (>1 means STR is faster)\n",
                   median(ratios, samples));
            puts("Includes call, ABI saves, preload/drain, loop control and store completion.");
            if (mhz > 0)
                printf("Cycle estimates assume fixed %.6g MHz; not a hardware cycle count.\n", mhz);
        }
    }
    free(src_raw);
    free(dst_raw);
    free(times[0]);
    free(times[1]);
    free(ratios);
    return ok ? EXIT_SUCCESS : EXIT_FAILURE;
}
