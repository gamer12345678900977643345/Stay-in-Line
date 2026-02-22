import pygame

start_screen = pygame.image.load("logo.png")
def show(screen, clock, highscore: int) -> bool:
    """
    Toont het startscherm.
    Geeft True terug als de speler wil starten, False als het venster gesloten wordt.
    """

    font_title  = pygame.font.SysFont(None, 80)
    font_sub    = pygame.font.SysFont(None, 36)
    font_small  = pygame.font.SysFont(None, 28)

    # Knop-rechthoek (wordt elk frame herberekend op basis van schermgrootte)
    running = True
    while running:
        screen_w, screen_h = screen.get_size()
        cx = screen_w // 2

        btn_w, btn_h = 220, 56
        btn_rect = pygame.Rect(cx - btn_w // 2, int(screen_h * 0.70), btn_w, btn_h)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    return True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if btn_rect.collidepoint(event.pos):
                    return True

        screen.fill((15, 15, 25))

        # ---- TITEL ----
        screen.blit(start_screen, start_screen.get_rect(centerx=cx, centery=int(screen_h * 0.5)))

        # ---- HIGHSCORE ----
        hs_text = f"Best: {highscore}" if highscore > 0 else "No record yet"
        hs_surf = font_sub.render(hs_text, True, (180, 180, 255))
        screen.blit(hs_surf, hs_surf.get_rect(centerx=cx, centery=int(screen_h * 0.42)))

        # ---- INSTRUCTIES ----
        instructions = [
            "Use  arrow keys  to move",
            "Less is more: Stay in the same lane to build your multiplier",
            "Switch lanes and the multiplier resets",
            "Don't crash!",
        ]
        for j, line in enumerate(instructions):
            surf = font_small.render(line, True, (200, 200, 200))
            screen.blit(surf, surf.get_rect(centerx=cx, centery=int(screen_h * 0.48) + j * 30))

        # ---- START KNOP ----
        mouse_pos = pygame.mouse.get_pos()
        btn_color = (60, 180, 80) if btn_rect.collidepoint(mouse_pos) else (40, 140, 60)
        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 255, 120), btn_rect, 2, border_radius=10)
        btn_surf = font_sub.render("START  /  SPACE", True, (255, 255, 255))
        screen.blit(btn_surf, btn_surf.get_rect(center=btn_rect.center))

        pygame.display.flip()
        clock.tick(60)

    return False