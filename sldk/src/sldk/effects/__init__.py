"""Effects system for SLDK.

Provides visual effects that can be applied to display content for enhanced
user experience. Effects are applied during the rendering process and can
create animations, transitions, and other visual enhancements.

This module includes both the new strategy-based effects system and the
legacy effects engine for backward compatibility.
"""

# New strategy-based effects system
from .base import Effect, EffectRegistry, register_effect, CompositeEffect, with_effect_mixin
from .reveal import RevealEffect, RevealCenterEffect
from .basic_transitions import (
    FadeInEffect, SlideInEffect, WipeEffect, 
    PulseEffect, FlashEffect
)

# Legacy effects engine (for backward compatibility)
from .effects import EffectsEngine, SimpleEffect
from .transitions import TransitionEngine, FadeTransition, WipeTransition
from .particles import ParticleEngine, Sparkle, RainDrop

__all__ = [
    # New strategy-based effects
    'Effect', 'EffectRegistry', 'register_effect', 'CompositeEffect', 'with_effect_mixin',
    'RevealEffect', 'RevealCenterEffect',
    'FadeInEffect', 'SlideInEffect', 'WipeEffect', 'PulseEffect', 'FlashEffect',
    
    # Legacy effects (backward compatibility)
    'EffectsEngine', 'SimpleEffect',
    'TransitionEngine', 'FadeTransition', 'WipeTransition', 
    'ParticleEngine', 'Sparkle', 'RainDrop'
]