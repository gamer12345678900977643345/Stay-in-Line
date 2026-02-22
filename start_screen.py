import pygame
import audio
from utils import resource_path

start_screen = pygame.image.load(resource_path("logo.png"))


def show(screen, clock, highscore: int) -> bool:
    font_sub   = pygame.font.SysFont(None, 36)
    font_small = pygame.font.SysFont(None, 28)

    running = True
    while running:
        screen_w, screen_h = screen.get_size()
        cx = screen_w // 2

        btn_w, btn_h = 220, 56
        btn_rect  = pygame.Rect(cx - btn_w // 2, int(screen_h * 0.70), btn_w, btn_h)
        mute_rect = audio.draw_mute_btn(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    audio.play_btn()
                    return True
                elif event.key == pygame.K_m:
                    audio.toggle()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if btn_rect.collidepoint(event.pos):
                    audio.play_btn()
                    return True
                elif mute_rect.collidepoint(event.pos):
                    audio.toggle()

        screen.fill((15, 15, 25))
        screen.blit(start_screen, start_screen.get_rect(centerx=cx, centery=int(screen_h * 0.5)))

        hs_text = f"Best: {highscore}" if highscore > 0 else "No record yet"
        hs_surf = font_sub.render(hs_text, True, (180, 180, 255))
        screen.blit(hs_surf, hs_surf.get_rect(centerx=cx, centery=int(screen_h * 0.42)))

        instructions = [
            "arrows to move   |   Less is more: stay in your lane",
            "Switch lanes = multiplier reset   |   Don't crash!",
        ]
        for j, line in enumerate(instructions):
            surf = font_small.render(line, True, (200, 200, 200))
            screen.blit(surf, surf.get_rect(centerx=cx, centery=int(screen_h * 0.48) + j * 30))

        mouse_pos = pygame.mouse.get_pos()
        btn_color = (60, 180, 80) if btn_rect.collidepoint(mouse_pos) else (40, 140, 60)
        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 255, 120), btn_rect, 2, border_radius=10)
        btn_surf = font_sub.render("START  /  SPACE", True, (255, 255, 255))
        screen.blit(btn_surf, btn_surf.get_rect(center=btn_rect.center))

        mute_rect = audio.draw_mute_btn(screen)
        pygame.display.flip()
        clock.tick(60)

    return False