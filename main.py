import pygame
import random
import genera
from obstacle import Obstacle

pygame.init()
screen = pygame.display.set_mode((genera.breedte, genera.hoogte), pygame.RESIZABLE)
clock = pygame.time.Clock()
running = True

ORIG_BREEDTE = genera.breedte
ORIG_HOOGTE = genera.hoogte

speed = 5
lane_offsets = [0, 0, 0]

obstacles = []
spawn_timer = 0
spawn_distance = 350

# ---- SPEELVELD (portrait) ----
# Het speelveld is een portret-rechthoek gecentreerd op het scherm.
# Verhouding: 9:16 (gsm-formaat). Pas FIELD_HEIGHT_RATIO aan om het groter/kleiner te maken.
FIELD_HEIGHT_RATIO = 0.95   # ← speelveld hoogte als % van schermhoogte
FIELD_ASPECT = 9 / 16       # ← breedte/hoogte verhouding (9:16 portrait)

# ---- PLAYER ----
motor_base = genera.motor_pic
PLAYER_STEP = 8
LANE_HYSTERESIS = 20

PLAYER_SIZE       = 0.2  # ← grootte motor sprite (% van speelveldhoogte)
PLAYER_HB_SCALE_X = 0.40  # ← breedte hitbox tov sprite
PLAYER_HB_SCALE_Y = 0.90  # ← hoogte hitbox tov sprite
PLAYER_Y_RATIO    = 0.78  # ← verticale positie speler in speelveld (0=top, 1=bottom)

# ---- OBSTACLE ----
OBS_SIZE       = 0.27  # ← grootte obstacle sprite (% van speelveldhoogte)
OBS_HB_SCALE_X = 0.40  # ← breedte obstacle hitbox tov sprite
OBS_HB_SCALE_Y = 0.90  # ← hoogte obstacle hitbox tov sprite

# ---- SCORING ----
score = 0.0
multiplier = 1.0
lane_ticks = 0
last_anchor_lane = 1
MULTIPLIER_BASE = 1.0
MULTIPLIER_GROWTH = 0.002
MULTIPLIER_CAP = 10.0

font_multiplier = pygame.font.SysFont(None, 28)
font_score = pygame.font.SysFont(None, 40)

frame = 0

# player_x is relatief aan speelveld (float, left edge van sprite)
player_x = None  # wordt eerste frame gezet

print("=== GAME START ===")
print(f"PLAYER_SIZE={PLAYER_SIZE} | PLAYER_HB_SCALE_X={PLAYER_HB_SCALE_X} | PLAYER_HB_SCALE_Y={PLAYER_HB_SCALE_Y}")
print(f"OBS_SIZE={OBS_SIZE} | OBS_HB_SCALE_X={OBS_HB_SCALE_X} | OBS_HB_SCALE_Y={OBS_HB_SCALE_Y}")
print(f"MULTIPLIER_GROWTH={MULTIPLIER_GROWTH} | PLAYER_STEP={PLAYER_STEP} | LANE_HYSTERESIS={LANE_HYSTERESIS}")


while running:
    dt = clock.tick(60) / 1000.0
    frame += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

    screen_width, screen_height = screen.get_size()

    # ---- SPEELVELD AFMETINGEN + POSITIE ----
    field_h = int(screen_height * FIELD_HEIGHT_RATIO)
    field_w = int(field_h * FIELD_ASPECT)
    field_x = (screen_width - field_w) // 2   # gecentreerd horizontaal
    field_y = (screen_height - field_h) // 2  # gecentreerd verticaal

    # Schaalfactoren relatief aan speelveld
    lane_width  = field_w // 3
    lane_height = field_h

    # Lane x-posities in schermcoördinaten
    lane_positions = [
        field_x,
        field_x + lane_width,
        field_x + lane_width * 2,
    ]

    # Initialiseer player_x op eerste frame (midden lane = lane 1)
    if player_x is None:
        player_x = float(lane_positions[1])

    # ---- PLAYER GROOTTE ----
    player_h = int(field_h * PLAYER_SIZE)
    player_w = player_h  # 1:1

    # ---- PLAYER BEWEGING ----
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= PLAYER_STEP
    if keys[pygame.K_RIGHT]:
        player_x += PLAYER_STEP

    # Clamp binnen speelveld
    player_x = max(float(field_x), min(player_x, float(field_x + field_w - player_w)))

    # ---- SCROLLING ----
    for i in range(3):
        lane_offsets[i] += speed
        if lane_offsets[i] >= lane_height:
            lane_offsets[i] -= lane_height

    # ---- TEKEN ACHTERGROND ----
    screen.fill((20, 20, 20))  # donkergrijs buiten speelveld

    # Speelveld achtergrond
    pygame.draw.rect(screen, (10, 10, 10), (field_x, field_y, field_w, field_h))

    # ---- TEKEN LANES + TILES ----
    # Clip alles binnen het speelveld
    field_surface = pygame.Surface((field_w, field_h))
    field_surface.fill((10, 10, 10))

    lane_img = pygame.transform.scale(genera.lane_pic, (lane_width, lane_height))
    tile_img = pygame.transform.scale(genera.tile_pic, (lane_width, lane_height))

    for i in range(3):
        lx = lane_width * i
        y_offset = lane_offsets[i]
        field_surface.blit(lane_img, (lx, y_offset - lane_height))
        field_surface.blit(lane_img, (lx, y_offset))
        if i < 2:
            field_surface.blit(tile_img, (lx, y_offset - lane_height))
            field_surface.blit(tile_img, (lx, y_offset))

    # ---- SPAWN OBSTACLES ----
    spawn_timer += speed
    if spawn_timer > spawn_distance:
        lane_index = random.randint(0, 2)

        obstacle_img = random.choice([
            genera.auto_b, genera.auto_g, genera.auto_p, genera.auto_r,
            genera.truck_b, genera.truck_g, genera.truck_p, genera.truck_r
        ])

        obs_h = int(field_h * OBS_SIZE)
        obs_w = obs_h  # 1:1

        obstacle_img_scaled = pygame.transform.scale(obstacle_img, (obs_w, obs_h))

        # x gecentreerd in lane, relatief aan speelveld
        lane_center_x = lane_width * lane_index + lane_width // 2
        obs_start_x = lane_center_x - obs_w // 2

        new_obs = Obstacle(
            lane_index,
            [lane_width * i for i in range(3)],
            obstacle_img_scaled,
            speed,
            -obs_h,
            override_x=obs_start_x
        )
        obstacles.append(new_obs)
        print(f"[frame {frame}] SPAWN | lane={lane_index} | size={obs_w}x{obs_h} | speed={speed:.2f} | total={len(obstacles)}")
        spawn_timer = 0

    # ---- UPDATE OBSTACLES ----
    before_cull = len(obstacles)
    for obstacle in obstacles:
        obstacle.update()  # geen scale_y nodig, we werken in speelveld-ruimte

    obstacles = [o for o in obstacles if not o.is_off_screen(field_h)]
    culled = before_cull - len(obstacles)
    if culled > 0:
        print(f"[frame {frame}] CULL {culled} | remaining={len(obstacles)}")

    # ---- OBSTACLE HITBOXEN ----
    obs_hitboxes = []
    for obstacle in obstacles:
        r = obstacle.rect
        hb_w = int(r.w * OBS_HB_SCALE_X)
        hb_h = int(r.h * OBS_HB_SCALE_Y)
        obs_hb = pygame.Rect(r.centerx - hb_w // 2, r.centery - hb_h // 2, hb_w, hb_h)
        obs_hitboxes.append((obstacle, obs_hb))

    # ---- DRAW OBSTACLES op field_surface ----
    for obstacle, obs_hb in obs_hitboxes:
        field_surface.blit(obstacle.image, (obstacle.x, int(obstacle.y)))
        pygame.draw.rect(field_surface, (255, 255, 0), obs_hb, 2)  # geel

    # ---- PLAYER in speelveld-coördinaten ----
    player_field_x = player_x - field_x  # omzetten naar speelveld-ruimte
    player_field_y = int(field_h * PLAYER_Y_RATIO)

    anchor_x_field = int(player_field_x + player_w / 2)

    player_rect_field = pygame.Rect(int(player_field_x), player_field_y, player_w, player_h)

    hb_w = int(player_w * PLAYER_HB_SCALE_X)
    hb_h = int(player_h * PLAYER_HB_SCALE_Y)
    hitbox_field = pygame.Rect(
        anchor_x_field - hb_w // 2,
        player_field_y + (player_h - hb_h) // 2,
        hb_w,
        hb_h,
    )

    # ---- LANE DETECTIE (in speelveld-ruimte) ----
    hysteresis = LANE_HYSTERESIS
    new_anchor_lane = last_anchor_lane

    lane_bounds = [lane_width * i for i in range(3)]

    if last_anchor_lane == 0:
        if anchor_x_field >= lane_bounds[1] + hysteresis:
            new_anchor_lane = 1
    elif last_anchor_lane == 1:
        if anchor_x_field < lane_bounds[1] - hysteresis:
            new_anchor_lane = 0
        elif anchor_x_field >= lane_bounds[2] + hysteresis:
            new_anchor_lane = 2
    elif last_anchor_lane == 2:
        if anchor_x_field < lane_bounds[2] - hysteresis:
            new_anchor_lane = 1

    if new_anchor_lane != last_anchor_lane:
        print(f"[frame {frame}] LANE SWITCH {last_anchor_lane} -> {new_anchor_lane} | was x{multiplier:.2f} after {lane_ticks} ticks")
        multiplier = 1.0
        lane_ticks = 0
        last_anchor_lane = new_anchor_lane

    # ---- DRAW PLAYER op field_surface ----
    motor_img = pygame.transform.scale(motor_base, (player_w, player_h))
    field_surface.blit(motor_img, player_rect_field.topleft)
    pygame.draw.rect(field_surface, (255, 0, 0), hitbox_field, 2)       # rood = player hitbox
    pygame.draw.circle(field_surface, (0, 255, 255), (anchor_x_field, player_rect_field.top), 4)  # cyaan = anchor

    # ---- COLLISION DETECTION ----
    for obstacle, obs_hb in obs_hitboxes:
        if hitbox_field.colliderect(obs_hb):
            print("=" * 40)
            print(f"[frame {frame}] COLLISION -> GAME OVER")
            print(f"  hitbox   : {hitbox_field}  ({hitbox_field.w}x{hitbox_field.h}px)")
            print(f"  obs_hb   : {obs_hb}  ({obs_hb.w}x{obs_hb.h}px)")
            print(f"  obs lane : {obstacle.lane_index}")
            print(f"  overlap_x: {max(0, min(hitbox_field.right, obs_hb.right) - max(hitbox_field.left, obs_hb.left))}px")
            print(f"  overlap_y: {max(0, min(hitbox_field.bottom, obs_hb.bottom) - max(hitbox_field.top, obs_hb.top))}px")
            print(f"  anchor_field_x={anchor_x_field} (lane {last_anchor_lane})")
            print(f"  score={int(score)} | multiplier=x{multiplier:.2f} | lane_ticks={lane_ticks}")
            print(f"  speed={speed:.3f} | frame={frame}")
            print("=" * 40)
            running = False
            break

    # ---- SPEELVELD RAND ----
    pygame.draw.rect(field_surface, (60, 60, 60), (0, 0, field_w, field_h), 2)

    # ---- BLIT SPEELVELD OP SCHERM ----
    screen.blit(field_surface, (field_x, field_y))

    # ---- UI (op scherm, buiten speelveld) ----
    # Multiplier boven speler (in schermcoördinaten)
    mult_surf = font_multiplier.render(f"x{multiplier:.2f}", True, (255, 220, 0))
    player_screen_cx = field_x + anchor_x_field
    player_screen_top = field_y + player_field_y
    mult_rect = mult_surf.get_rect(centerx=player_screen_cx, bottom=player_screen_top - 4)
    screen.blit(mult_surf, mult_rect)

    # Score links naast speelveld (of boven als er geen ruimte is)
    score_surf = font_score.render(f"{int(score)}", True, (255, 255, 255))
    screen.blit(score_surf, (max(8, field_x - score_surf.get_width() - 8), field_y + 8))

    # ---- MULTIPLIER + SCORE ----
    lane_ticks += 1
    multiplier = min(MULTIPLIER_BASE * (1 + MULTIPLIER_GROWTH) ** lane_ticks, MULTIPLIER_CAP)
    score += multiplier * dt * 10

    if frame % 60 == 0:
        print(f"[frame {frame}] STATUS | lane={last_anchor_lane} | ticks={lane_ticks} | x{multiplier:.2f} | score={int(score)} | speed={speed:.3f} | obs={len(obstacles)}")

    speed += 0.001
    pygame.display.flip()

print(f"=== GAME OVER | final score={int(score)} | frames={frame} ===")
pygame.quit()