import pygame
import json
import os

import start_screen
import end_screen
import game

HIGHSCORE_FILE = "highscore.json"


def load_highscore() -> int:
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(json.load(f).get("highscore", 0))
        except Exception:
            pass
    return 0


def save_highscore(score: int):
    with open(HIGHSCORE_FILE, "w") as f:
        json.dump({"highscore": score}, f)


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 800), pygame.RESIZABLE)
    pygame.display.set_caption("Stay in Lane")
    clock = pygame.time.Clock()

    highscore = load_highscore()

    while True:
        # ---- STARTSCHERM ----
        start = start_screen.show(screen, clock, highscore)
        if not start:
            break  # venster gesloten

        # ---- GAME ----
        score = game.run(screen, clock)

        # ---- HIGHSCORE BIJWERKEN ----
        if score > highscore:
            highscore = score
            save_highscore(highscore)

        # ---- EINDSCHERM ----
        result = end_screen.show(screen, clock, score, highscore)
        if result == "quit":
            break
        # result == "restart" -> loop terug naar startscherm

    pygame.quit()


if __name__ == "__main__":
    main()