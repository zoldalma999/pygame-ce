#include "simd_image.h"

#if defined(HAVE_IMMINTRIN_H) && !defined(SDL_DISABLE_IMMINTRIN_H)
#include <immintrin.h>
#endif /* defined(HAVE_IMMINTRIN_H) && !defined(SDL_DISABLE_IMMINTRIN_H) */

#define BAD_AVX2_FUNCTION_CALL                                               \
    printf(                                                                  \
        "Fatal Error: Attempted calling an AVX2 function when both compile " \
        "time and runtime support is missing. If you are seeing this "       \
        "message, you have stumbled across a pygame bug, please report it "  \
        "to the devs!");                                                     \
    PG_EXIT(1)

/* helper function that does a runtime check for AVX2. It has the added
 * functionality of also returning 0 if compile time support is missing */
int
pg_has_avx2()
{
#if defined(__AVX2__) && defined(HAVE_IMMINTRIN_H) && \
    !defined(SDL_DISABLE_IMMINTRIN_H)
    return SDL_HasAVX2();
#else
    return 0;
#endif /* defined(__AVX2__) && defined(HAVE_IMMINTRIN_H) && \
          !defined(SDL_DISABLE_IMMINTRIN_H) */
}

/* This returns 1 when avx2 is available at runtime but support for it isn't
 * compiled in, 0 in all other cases */
int
pg_avx2_at_runtime_but_uncompiled()
{
    if (SDL_HasAVX2()) {
#if defined(__AVX2__) && defined(HAVE_IMMINTRIN_H) && \
    !defined(SDL_DISABLE_IMMINTRIN_H)
        return 0;
#else
        return 1;
#endif /* defined(__AVX2__) && defined(HAVE_IMMINTRIN_H) && \
          !defined(SDL_DISABLE_IMMINTRIN_H) */
    }
    return 0;
}

#if defined(__AVX2__) && defined(HAVE_IMMINTRIN_H) && \
    !defined(SDL_DISABLE_IMMINTRIN_H)

__m256i
create_general_shuffle_mask(int src_r, int src_g, int src_b, int src_a,
                            int dst_r, int dst_g, int dst_b, int dst_a)
{
    uint8_t control[16];

    int dst_to_src[4];
    dst_to_src[dst_r] = src_r;
    dst_to_src[dst_g] = src_g;
    dst_to_src[dst_b] = src_b;
    dst_to_src[dst_a] = src_a;

    for (int i = 0; i < 4; ++i) {
        int base = i * 4;
        for (int j = 0; j < 4; j++) {
            control[base + j] = base + dst_to_src[j];
        }
    }

    return _mm256_broadcastsi128_si256(_mm_loadu_si128((__m128i *)control));
}

void
tobytes_avx2(SDL_Surface *surf, PG_PixelFormat *src_fmt, int flipped,
             Uint32 *dstp, char rindex, char gindex, char bindex, char aindex)
{
    int s_row_skip = (surf->pitch - surf->w * 4) / 4;

    int pixel_batch_length = surf->w * surf->h;
    int num_batches = 1;

    Uint32 *srcp = (Uint32 *)surf->pixels;

    if (s_row_skip > 0 || flipped) {
        pixel_batch_length = surf->w;
        num_batches = surf->h;

        if (flipped) {
            s_row_skip = -surf->pitch / 4 - surf->w;
            srcp = (Uint32 *)(surf->pixels) + surf->pitch / 4 * (surf->h - 1);
        }
    }
    int remaining_pixels = pixel_batch_length % 8;
    int perfect_8_pixels = pixel_batch_length / 8;

    int perfect_8_pixels_batch_counter = perfect_8_pixels;
    int remaining_pixels_batch_counter = remaining_pixels;

    __m256i *srcp256 = (__m256i *)srcp;
    __m256i *dstp256 = (__m256i *)dstp;
    // If there's no alpha channel, write 255 on all alpha values
    __m256i alpha_mask = src_fmt->Amask == 0
                             ? _mm256_set1_epi32(255 << (aindex * 8))
                             : _mm256_set1_epi32(0);

    __m256i mm256_src, mm256_shuffle_control;

    mm256_shuffle_control = create_general_shuffle_mask(
        src_fmt->Rshift / 8, src_fmt->Gshift / 8, src_fmt->Bshift / 8,
        src_fmt->Ashift / 8, rindex, gindex, bindex, aindex);

    __m256i _partial8_mask = _mm256_set_epi32(
        0x00, (remaining_pixels > 6) ? -1 : 0, (remaining_pixels > 5) ? -1 : 0,
        (remaining_pixels > 4) ? -1 : 0, (remaining_pixels > 3) ? -1 : 0,
        (remaining_pixels > 2) ? -1 : 0, (remaining_pixels > 1) ? -1 : 0,
        (remaining_pixels > 0) ? -1 : 0);

    while (num_batches--) {
        perfect_8_pixels_batch_counter = perfect_8_pixels;
        remaining_pixels_batch_counter = remaining_pixels;
        while (perfect_8_pixels_batch_counter--) {
            mm256_src = _mm256_loadu_si256(srcp256);
            _mm256_storeu_si256(
                dstp256, _mm256_or_si256(_mm256_shuffle_epi8(
                                             mm256_src, mm256_shuffle_control),
                                         alpha_mask));
            srcp256++;
            dstp256++;
        }
        srcp = (Uint32 *)srcp256;
        dstp = (Uint32 *)dstp256;
        if (remaining_pixels_batch_counter > 0) {
            mm256_src = _mm256_maskload_epi32((int *)srcp, _partial8_mask);

            _mm256_maskstore_epi32(
                (int *)dstp, _partial8_mask,
                _mm256_or_si256(
                    _mm256_shuffle_epi8(mm256_src, mm256_shuffle_control),
                    alpha_mask));

            srcp += remaining_pixels_batch_counter;
            dstp += remaining_pixels_batch_counter;
        }
        srcp += s_row_skip;
        srcp256 = (__m256i *)srcp;
        dstp256 = (__m256i *)dstp;
    }
}

#else

void
tobytes_avx2(SDL_Surface *surf, PG_PixelFormat *src_fmt, int flipped,
             Uint32 *dstp, char rindex, char gindex, char bindex, char aindex)
{
    BAD_AVX2_FUNCTION_CALL;
}

#endif
