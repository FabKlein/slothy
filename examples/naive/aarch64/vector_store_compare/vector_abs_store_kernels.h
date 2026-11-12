#ifndef VECTOR_ABS_STORE_KERNELS_H
#define VECTOR_ABS_STORE_KERNELS_H

#include <stddef.h>
#include <stdint.h>

/* One block is 64 FP32 bit patterns (256 bytes). Buffers must not overlap.
 * Both functions do nothing for blocks < 2; no partial block is processed.
 * Clear the sign bit without interpreting the values as C floating point.
 */
void vector_abs_st1(uint32_t *restrict dst, const uint32_t *restrict src,
                    size_t blocks);
void vector_abs_str(uint32_t *restrict dst, const uint32_t *restrict src,
                    size_t blocks);

#endif
