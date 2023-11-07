#include <SDL_Mixer.h>
#include "mixer.h"

void
apply_effect(int channel, pgEffect *effect)
{
    switch (effect->id) {
        case pgEffect_VolumeID:
            Mix_SetPanning(channel, ((pgEffect_Volume *)(effect->data))->left,
                           ((pgEffect_Volume *)(effect->data))->right);
            break;

        case pgEffect_PositionID:
            Mix_SetPosition(channel,
                            ((pgEffect_Position *)(effect->data))->angle,
                            ((pgEffect_Position *)(effect->data))->distance);
            break;

        case pgEffect_RevereseStereoID:
            Mix_SetReverseStereo(
                channel, ((pgEffect_RevereseStereo *)(effect->data))->flipped);
            break;

        case pgEffect_CustomID:
            Mix_RegisterEffect(channel, effect->func, effect->done,
                               effect->data);
            break;

        default:
            printf("Unknown effect %d, skipping...\n", effect->id);
            break;
    }
}

void
apply_effects(int channel, pgEffect *effects)
{
    pgEffect *effect = effects;
    while (effect->next) {
        apply_effect(channel, effect);
        effect = effect->next;
    }
}
