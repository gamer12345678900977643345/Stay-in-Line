import pygame
import audio
from utils import resource_path

end_screen_img = pygame.image.load(resource_path("game over.png"))
trophy_img     = pygame.image.load(resource_path("trofee.png"))


def show(screen, clock, score: int, highscore: int) -> str:
    font_score = pygame.font.SysFont("ocraextended", 52)
    font_sub   = pygame.font.SysFont("ocraextended", 36)
    font_small = pygame.font.SysFont("ocraextended", 28)

    is_new_record = score >= highscore and score > 0

    running = True
    while running:
        screen_w, screen_h = screen.get_size()
        cx = screen_w // 2

        btn_w, btn_h = 220, 56
        btn_rect  = pygame.Rect(cx - btn_w // 2, int(screen_h * 0.72), btn_w, btn_h)
        mute_rect = audio.draw_mute_btn(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    audio.play_btn()
                    return "restart"
                elif event.key == pygame.K_ESCAPE:
                    return "quit"
                elif event.key == pygame.K_m:
                    audio.toggle()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if btn_rect.collidepoint(event.pos):
                    audio.play_btn()
                    return "restart"
                elif mute_rect.collidepoint(event.pos):
                    audio.toggle()

        screen.fill((20, 10, 10))
        screen.blit(end_screen_img, end_screen_img.get_rect(centerx=cx, centery=int(screen_h * 0.50)))

        score_surf = font_score.render(f"Score:  {score}", True, (255, 255, 255))
        screen.blit(score_surf, score_surf.get_rect(centerx=cx, centery=int(screen_h * 0.4)))

        if is_new_record:
            trophy_size   = 80
            trophy_scaled = pygame.transform.smoothscale(trophy_img, (trophy_size, trophy_size + 15))
            hs_text_surf  = font_sub.render("  New record!", True, (255, 220, 0))
            total_w       = trophy_size + hs_text_surf.get_width()
            start_x       = cx - total_w // 2
            y_center      = int(screen_h * 0.48)
            screen.blit(trophy_scaled, (start_x, y_center - trophy_size // 2))
            screen.blit(hs_text_surf, (start_x + trophy_size, y_center - hs_text_surf.get_height() // 2))
        else:
            hs_surf = font_sub.render(f"Best:  {highscore}", True, (180, 180, 255))
            screen.blit(hs_surf, hs_surf.get_rect(centerx=cx, centery=int(screen_h * 0.48)))

        hint_surf = font_small.render("ESC to quit", True, (120, 120, 120))
        screen.blit(hint_surf, hint_surf.get_rect(centerx=cx, centery=int(screen_h * 0.86)))

        mouse_pos = pygame.mouse.get_pos()
        btn_color = (60, 120, 220) if btn_rect.collidepoint(mouse_pos) else (40, 80, 180)
        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 160, 255), btn_rect, 2, border_radius=10)
        btn_surf = font_sub.render("RESTART  /  SPACE", True, (255, 255, 255))
        screen.blit(btn_surf, btn_surf.get_rect(center=btn_rect.center))

        mute_rect = audio.draw_mute_btn(screen)
        pygame.display.flip()
        clock.tick(60)

    return "quit"