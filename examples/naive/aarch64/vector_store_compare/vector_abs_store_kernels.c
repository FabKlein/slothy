#include "vector_abs_store_kernels.h"

/* Keep the schedule, registers and addressing identical. Only the store
 * encoding changes: a single-register structure store versus an ordinary Q
 * store. The preload/drain make every call independent of previous calls.
 */
#define ST1(reg) "st1 {v" #reg ".4s}, [%[dst]], #16\n\t"
#define STR(reg) "str q" #reg ", [%[dst]], #16\n\t"
#define BIC(reg) "bic v" #reg ".4s, #0x80, lsl #24\n\t"
#define LDP(a, b) "ldp q" #a ", q" #b ", [%[src]], #32\n\t"

#define PRELOAD                          \
    LDP(30, 19)                         \
    LDP(2, 14)                          \
    LDP(11, 0)                          \
    LDP(22, 4)                          \
    LDP(27, 10)                         \
    LDP(28, 23)                         \
    BIC(30)                             \
    LDP(16, 15)                         \
    BIC(2)                              \
    BIC(19)                             \
    LDP(18, 6)                          \
    "sub %[count], %[count], #1\n\t"    \
    "b 1f\n\t"                        \
    ".balign 64\n\t"                  \
    ".space 60\n\t"                   \
    "1:\n\t"

/* The first instruction is at offset 60 modulo 64 for both variants.
 * Padding above is skipped, not executed. Each iteration handles 64 floats.
 */
#define BODY(STORE)                      \
    STORE(30)                           \
    BIC(14)                             \
    STORE(19)                           \
    BIC(11)                             \
    LDP(30, 19)                         \
    BIC(0)                              \
    BIC(23)                             \
    STORE(2)                            \
    STORE(14)                           \
    BIC(27)                             \
    STORE(11)                           \
    BIC(22)                             \
    STORE(0)                            \
    BIC(4)                              \
    BIC(28)                             \
    LDP(2, 14)                          \
    LDP(11, 0)                          \
    BIC(10)                             \
    STORE(22)                           \
    STORE(4)                            \
    BIC(16)                             \
    BIC(15)                             \
    STORE(27)                           \
    BIC(30)                             \
    STORE(10)                           \
    LDP(22, 4)                          \
    BIC(2)                              \
    BIC(19)                             \
    LDP(27, 10)                         \
    STORE(28)                           \
    BIC(6)                              \
    BIC(18)                             \
    STORE(23)                           \
    LDP(28, 23)                         \
    STORE(16)                           \
    STORE(15)                           \
    LDP(16, 15)                         \
    STORE(18)                           \
    STORE(6)                            \
    LDP(18, 6)                          \
    "subs %[count], %[count], #1\n\t"   \
    "cbnz %[count], 1b\n\t"

#define DRAIN(STORE)                     \
    BIC(18)                             \
    BIC(14)                             \
    STORE(30)                           \
    BIC(11)                             \
    STORE(19)                           \
    BIC(0)                              \
    STORE(2)                            \
    BIC(22)                             \
    STORE(14)                           \
    BIC(4)                              \
    STORE(11)                           \
    BIC(27)                             \
    STORE(0)                            \
    BIC(10)                             \
    STORE(22)                           \
    BIC(28)                             \
    STORE(4)                            \
    BIC(23)                             \
    STORE(27)                           \
    BIC(16)                             \
    STORE(10)                           \
    BIC(15)                             \
    BIC(6)                              \
    STORE(28)                           \
    STORE(23)                           \
    STORE(16)                           \
    STORE(15)                           \
    STORE(18)                           \
    STORE(6)

/* Early-clobber operands keep the three live GPRs distinct. Declaring all
 * scratch vectors lets the compiler preserve the ABI's callee-saved halves.
 */
#define OPERANDS                                                       \
    : [src] "+&r"(src), [dst] "+&r"(dst), [count] "+&r"(blocks)       \
    :                                                                  \
    : "cc", "memory", "v0", "v2", "v4", "v6", "v10", "v11", "v14", \
      "v15", "v16", "v18", "v19", "v22", "v23", "v27", "v28", "v30"

__attribute__((noinline, aligned(64)))
void vector_abs_st1(uint32_t *restrict dst, const uint32_t *restrict src,
                    size_t blocks)
{
    if (blocks < 2)
        return;
    __asm__ volatile(PRELOAD BODY(ST1) DRAIN(ST1) OPERANDS);
}

__attribute__((noinline, aligned(64)))
void vector_abs_str(uint32_t *restrict dst, const uint32_t *restrict src,
                    size_t blocks)
{
    if (blocks < 2)
        return;
    __asm__ volatile(PRELOAD BODY(STR) DRAIN(STR) OPERANDS);
}
