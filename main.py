import pygame
import json
import audio
import start_screen
import end_screen
import game
from utils import resource_path, highscore_path

HIGHSCORE_FILE = highscore_path()


def load_highscore() -> int:
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return int(json.load(f).get("highscore", 0))
    except Exception:
        return 0


def save_highscore(score: int):
    with open(HIGHSCORE_FILE, "w") as f:
        json.dump({"highscore": score}, f)


def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((1280, 800), pygame.RESIZABLE)
    pygame.display.set_caption("Stay in Lane")
    clock = pygame.time.Clock()

    pygame.mixer.music.load(resource_path("soundtrack.ogg"))
    pygame.mixer.music.play(loops=-1)

    btn_sfx = pygame.mixer.Sound(resource_path("designed, braam, synth, braams, brahm, resonant chorus bass (c) 01.wav"))
    audio.init(btn_sfx)

    highscore = load_highscore()

    while True:
        start = start_screen.show(screen, clock, highscore)
        if not start:
            break

        score = game.run(screen, clock)

        if score > highscore:
            highscore = score
            save_highscore(highscore)

        result = end_screen.show(screen, clock, score, highscore)
        if result == "quit":
            break

    pygame.quit()


if __name__ == "__main__":
    main()