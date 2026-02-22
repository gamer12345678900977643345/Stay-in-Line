import pygame
from utils import resource_path

MUSIC_VOLUME  = 0.6
SFX_VOLUME    = 0.8
ENGINE_VOLUME = 0.4
CRASH_VOLUME  = 0.9

_muted       = False
_btn_sfx     = None
_icon_mute   = None
_icon_unmute = None
_engine_sfx  = None
_crash_sfx   = None


def init(btn_sfx_sound: pygame.mixer.Sound):
    global _btn_sfx, _icon_mute, _icon_unmute
    _btn_sfx     = btn_sfx_sound
    _icon_mute   = pygame.image.load(resource_path("mute.png")).convert_alpha()
    _icon_unmute = pygame.image.load(resource_path("unmute.png")).convert_alpha()
    _apply()


def register_game_sounds(engine: pygame.mixer.Sound = None, crash: pygame.mixer.Sound = None):
    global _engine_sfx, _crash_sfx
    _engine_sfx = engine
    _crash_sfx  = crash
    _apply()


def unregister_game_sounds():
    global _engine_sfx, _crash_sfx
    _engine_sfx = None
    _crash_sfx  = None


def is_muted() -> bool:
    return _muted


def toggle():
    global _muted
    _muted = not _muted
    _apply()


def play_btn():
    if _btn_sfx and not _muted:
        _btn_sfx.play()


def _apply():
    pygame.mixer.music.set_volume(0.0 if _muted else MUSIC_VOLUME)
    if _btn_sfx:
        _btn_sfx.set_volume(0.0 if _muted else SFX_VOLUME)
    if _engine_sfx:
        _engine_sfx.set_volume(0.0 if _muted else ENGINE_VOLUME)
    if _crash_sfx:
        _crash_sfx.set_volume(0.0 if _muted else CRASH_VOLUME)


def draw_mute_btn(screen: pygame.Surface) -> pygame.Rect:
    screen_w, screen_h = screen.get_size()
    size   = 40
    margin = 12
    rect   = pygame.Rect(screen_w - size - margin, margin, size, size)

    color  = (60, 60, 60) if _muted else (40, 40, 40)
    border = (120, 120, 120) if _muted else (200, 200, 200)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, border, rect, 2, border_radius=8)

    icon = _icon_mute if _muted else _icon_unmute
    if icon:
        icon_scaled = pygame.transform.smoothscale(icon, (size - 10, size - 10))
        screen.blit(icon_scaled, icon_scaled.get_rect(center=rect.center))

    return rect