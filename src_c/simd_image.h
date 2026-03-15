#define NO_PYGAME_C_API
#include "_surface.h"

// AVX2 functions

void
tobytes_avx2(SDL_Surface *surf, PG_PixelFormat *src_fmt, int flipped,
             Uint32 *dstp, char rindex, char gindex, char bindex, char aindex);
