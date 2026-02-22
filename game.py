import pygame
import random
import genera
from obstacle import Obstacle

# ---- INSTELBARE WAARDEN ----
FIELD_HEIGHT_RATIO = 0.95
FIELD_ASPECT       = 9 / 16

PLAYER_STEP        = 8
LANE_HYSTERESIS    = 20
PLAYER_SIZE        = 0.2
PLAYER_HB_SCALE_X  = 0.40
PLAYER_HB_SCALE_Y  = 0.90
PLAYER_Y_RATIO     = 0.78

OBS_SIZE           = 0.28
OBS_HB_SCALE_X     = 0.40
OBS_HB_SCALE_Y     = 0.90

MULTIPLIER_BASE    = 1.0
MULTIPLIER_GROWTH  = 0.002
MULTIPLIER_CAP     = 10.0


def run(screen, clock):
    """Start de game loop. Geeft de finale score terug als int."""

    speed       = 5.0
    road_offset = 0.0   # scrollpositie van het wegdek (0..field_h)
    obstacles   = []
    spawn_timer  = 0
    spawn_distance = 350

    motor_base = genera.motor_pic

    score            = 0.0
    multiplier       = 1.0
    lane_ticks       = 0
    last_anchor_lane = 1
    player_x         = None   # gezet op eerste frame
    frame            = 0
    running          = True

    font_multiplier = pygame.font.SysFont(None, 28)
    font_score      = pygame.font.SysFont(None, 40)

    print("=== GAME START ===")
    print(f"PLAYER_SIZE={PLAYER_SIZE} | HB_X={PLAYER_HB_SCALE_X} | HB_Y={PLAYER_HB_SCALE_Y}")
    print(f"OBS_SIZE={OBS_SIZE} | OBS_HB_X={OBS_HB_SCALE_X} | OBS_HB_Y={OBS_HB_SCALE_Y}")

    while running:
        dt     = clock.tick(60) / 1000.0
        frame += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        screen_width, screen_height = screen.get_size()

        # ---- SPEELVELD ----
        field_h = int(screen_height * FIELD_HEIGHT_RATIO)
        field_w = int(field_h * FIELD_ASPECT)
        field_x = (screen_width - field_w) // 2
        field_y = (screen_height - field_h) // 2

        lane_width  = field_w // 3
        lane_height = field_h
        lane_bounds = [lane_width * i for i in range(3)]

        # Lane x-posities in schermcoördinaten (voor initialisatie player_x)
        lane_screen_positions = [field_x + lane_width * i for i in range(3)]

        if player_x is None:
            player_x = float(lane_screen_positions[1])

        # ---- PLAYER GROOTTE ----
        player_h = int(field_h * PLAYER_SIZE)
        player_w = player_h

        # ---- PLAYER BEWEGING ----
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= PLAYER_STEP
        if keys[pygame.K_RIGHT]:
            player_x += PLAYER_STEP

        player_x = max(float(field_x), min(player_x, float(field_x + field_w - player_w)))

        # ---- SCROLLING ----
        road_offset += speed
        if road_offset >= field_h:
            road_offset -= field_h

        # ---- ACHTERGROND ----
        screen.fill((20, 20, 20))

        # ---- FIELD SURFACE ----
        field_surface = pygame.Surface((field_w, field_h))

        # Schaal road_pic naar speelveldgrootte en scroll via dubbele blit
        road_img = pygame.transform.scale(genera.road_pic, (field_w, field_h))
        field_surface.blit(road_img, (0, road_offset - field_h))   # kopie hierboven
        field_surface.blit(road_img, (0, road_offset))              # huidige positie

        # ---- SPAWN OBSTACLES ----
        spawn_timer += speed
        if spawn_timer > spawn_distance:
            lane_index   = random.randint(0, 2)
            obstacle_img = random.choice([
                genera.auto_b, genera.auto_g, genera.auto_p, genera.auto_r,
                genera.truck_b, genera.truck_g, genera.truck_p, genera.truck_r
            ])

            obs_h = int(field_h * OBS_SIZE)
            obs_w = obs_h

            obstacle_img_scaled = pygame.transform.scale(obstacle_img, (obs_w, obs_h))
            lane_center_x       = lane_width * lane_index + lane_width // 2
            obs_start_x         = lane_center_x - obs_w // 2

            new_obs = Obstacle(
                lane_index,
                lane_bounds,
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
            obstacle.update()

        obstacles = [o for o in obstacles if not o.is_off_screen(field_h)]
        culled    = before_cull - len(obstacles)
        if culled > 0:
            print(f"[frame {frame}] CULL {culled} | remaining={len(obstacles)}")

        # ---- OBSTACLE HITBOXEN ----
        obs_hitboxes = []
        for obstacle in obstacles:
            r    = obstacle.rect
            hb_w = int(r.w * OBS_HB_SCALE_X)
            hb_h = int(r.h * OBS_HB_SCALE_Y)
            obs_hb = pygame.Rect(r.centerx - hb_w // 2, r.centery - hb_h // 2, hb_w, hb_h)
            obs_hitboxes.append((obstacle, obs_hb))

        # ---- DRAW OBSTACLES ----
        for obstacle, obs_hb in obs_hitboxes:
            field_surface.blit(obstacle.image, (obstacle.x, int(obstacle.y)))
            pygame.draw.rect(field_surface, (255, 255, 0), obs_hb, 2)

        # ---- PLAYER (speelveld-coördinaten) ----
        player_field_x = player_x - field_x
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

        # ---- LANE DETECTIE ----
        new_anchor_lane = last_anchor_lane

        if last_anchor_lane == 0:
            if anchor_x_field >= lane_bounds[1] + LANE_HYSTERESIS:
                new_anchor_lane = 1
        elif last_anchor_lane == 1:
            if anchor_x_field < lane_bounds[1] - LANE_HYSTERESIS:
                new_anchor_lane = 0
            elif anchor_x_field >= lane_bounds[2] + LANE_HYSTERESIS:
                new_anchor_lane = 2
        elif last_anchor_lane == 2:
            if anchor_x_field < lane_bounds[2] - LANE_HYSTERESIS:
                new_anchor_lane = 1

        if new_anchor_lane != last_anchor_lane:
            print(f"[frame {frame}] LANE SWITCH {last_anchor_lane} -> {new_anchor_lane} | was x{multiplier:.2f} after {lane_ticks} ticks")
            multiplier       = 1.0
            lane_ticks       = 0
            last_anchor_lane = new_anchor_lane

        # ---- DRAW PLAYER ----
        motor_img = pygame.transform.scale(motor_base, (player_w, player_h))
        field_surface.blit(motor_img, player_rect_field.topleft)
        pygame.draw.rect(field_surface, (255, 0, 0), hitbox_field, 2)
        pygame.draw.circle(field_surface, (0, 255, 255), (anchor_x_field, player_rect_field.top), 4)

        # ---- COLLISION ----
        for obstacle, obs_hb in obs_hitboxes:
            if hitbox_field.colliderect(obs_hb):
                print("=" * 40)
                print(f"[frame {frame}] COLLISION -> GAME OVER")
                print(f"  hitbox   : {hitbox_field} ({hitbox_field.w}x{hitbox_field.h}px)")
                print(f"  obs_hb   : {obs_hb} ({obs_hb.w}x{obs_hb.h}px)")
                print(f"  obs lane : {obstacle.lane_index}")
                print(f"  overlap_x: {max(0, min(hitbox_field.right, obs_hb.right) - max(hitbox_field.left, obs_hb.left))}px")
                print(f"  overlap_y: {max(0, min(hitbox_field.bottom, obs_hb.bottom) - max(hitbox_field.top, obs_hb.top))}px")
                print(f"  score={int(score)} | multiplier=x{multiplier:.2f} | lane_ticks={lane_ticks}")
                print(f"  speed={speed:.3f} | frame={frame}")
                print("=" * 40)
                running = False
                break

        # ---- RAND + BLIT ----
        pygame.draw.rect(field_surface, (60, 60, 60), (0, 0, field_w, field_h), 2)
        screen.blit(field_surface, (field_x, field_y))

        # ---- UI ----
        mult_surf = font_multiplier.render(f"x{multiplier:.2f}", True, (255, 220, 0))
        mult_rect = mult_surf.get_rect(
            centerx=field_x + anchor_x_field,
            bottom=field_y + player_field_y - 4
        )
        screen.blit(mult_surf, mult_rect)

        score_surf = font_score.render(f"{int(score)}", True, (255, 255, 255))
        screen.blit(score_surf, (max(8, field_x - score_surf.get_width() - 8), field_y + 8))

        # ---- MULTIPLIER + SCORE UPDATE ----
        lane_ticks += 1
        multiplier  = min(MULTIPLIER_BASE * (1 + MULTIPLIER_GROWTH) ** lane_ticks, MULTIPLIER_CAP)
        score      += multiplier * dt * 10

        if frame % 60 == 0:
            print(f"[frame {frame}] STATUS | lane={last_anchor_lane} | x{multiplier:.2f} | score={int(score)} | speed={speed:.3f}")

        speed += 0.001
        pygame.display.flip()

    print(f"=== GAME OVER | final score={int(score)} | frames={frame} ===")
    return int(score)