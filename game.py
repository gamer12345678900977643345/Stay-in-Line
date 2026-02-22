import pygame
import random
import genera
import audio
from obstacle import Obstacle
from utils import resource_path

FIELD_HEIGHT_RATIO = 0.99
FIELD_ASPECT       = 9 / 16

PLAYER_STEP        = 8
LANE_HYSTERESIS    = 20
PLAYER_SIZE        = 0.21
PLAYER_HB_SCALE_X  = 0.38
PLAYER_HB_SCALE_Y  = 0.88
PLAYER_Y_RATIO     = 0.7

OBS_SIZE           = 0.29
OBS_HB_SCALE_X     = 0.38
OBS_HB_SCALE_Y     = 0.88

MULTIPLIER_BASE   = 1.0
MULTIPLIER_GROWTH = 0.002
MULTIPLIER_CAP    = 10.0

# trail
TRAIL_LENGTH = 45
TRAIL_WIDTH  = 0.18
TRAIL_COLOR  = (0, 200, 255)
TRAIL_GLOW   = (150, 240, 255)

# squish
SQUISH_SCALE_X = 1.18
SQUISH_SCALE_Y = 0.86
SQUISH_SPEED   = 0.18

# screen shake
SHAKE_FRAMES    = 5
SHAKE_INTENSITY = 6

# multiplier pop
MULT_POP_SCALE  = 1.6
MULT_POP_FRAMES = 8

# speed lines
SPEED_LINE_COUNT = 6
SPEED_LINE_ALPHA = 60
SPEED_LINE_WIDTH = 2


def run(screen, clock):
    speed          = 5.0
    road_offset    = 0.0
    obstacles      = []
    spawn_timer    = 0
    spawn_distance = 350
    motor_base     = genera.motor_pic

    motor_channel = pygame.mixer.Channel(2)
    crash_channel = pygame.mixer.Channel(3)
    motor_sfx = pygame.mixer.Sound(resource_path("engine.ogg"))
    motor_sfx.set_volume(0.0 if audio.is_muted() else 0.4)
    motor_channel.play(motor_sfx, loops=-1)
    crash_sfx = pygame.mixer.Sound(resource_path("crash.ogg"))
    crash_sfx.set_volume(0.0 if audio.is_muted() else 0.9)
    audio.register_game_sounds(engine=motor_sfx, crash=crash_sfx)

    score                = 0.0
    multiplier           = 1.0
    last_multiplier      = 1.0
    lane_ticks           = 0
    last_anchor_lane     = 1
    player_x             = None
    frame                = 0
    running              = True
    trail                = []
    squish_x             = 1.0
    squish_y             = 1.0
    mult_pop_frames_left = 0
    last_field_surface   = None
    last_field_x = last_field_y = 0

    font_score = pygame.font.Font(resource_path("DejaVuSansMono-Bold.ttf"), 24)

    while running:
        dt     = clock.tick(60) / 1000.0
        frame += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                motor_channel.stop()
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        screen_width, screen_height = screen.get_size()

        field_h = int(screen_height * FIELD_HEIGHT_RATIO)
        field_w = int(field_h * FIELD_ASPECT)
        field_x = (screen_width - field_w) // 2
        field_y = (screen_height - field_h) // 2

        lane_width  = field_w // 3
        lane_bounds = [lane_width * i for i in range(3)]
        lane_screen_positions = [field_x + lane_width * i for i in range(3)]

        if player_x is None:
            player_x = float(lane_screen_positions[1])

        player_h = int(field_h * PLAYER_SIZE)
        player_w = player_h

        # movement + squish
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= PLAYER_STEP
            squish_x = SQUISH_SCALE_X
            squish_y = SQUISH_SCALE_Y
        elif keys[pygame.K_RIGHT]:
            player_x += PLAYER_STEP
            squish_x = SQUISH_SCALE_X
            squish_y = SQUISH_SCALE_Y
        else:
            squish_x += (1.0 - squish_x) * SQUISH_SPEED
            squish_y += (1.0 - squish_y) * SQUISH_SPEED

        player_x = max(float(field_x), min(player_x, float(field_x + field_w - player_w)))

        # road scroll
        road_offset += speed
        if road_offset >= field_h:
            road_offset -= field_h

        # trail
        for pt in trail:
            pt[1] += speed
        player_field_x = player_x - field_x
        player_field_y = int(field_h * PLAYER_Y_RATIO)
        anchor_x_field = int(player_field_x + player_w / 2)
        trail.append([anchor_x_field, player_field_y + player_h])
        if len(trail) > TRAIL_LENGTH:
            trail.pop(0)
        trail = [pt for pt in trail if pt[1] < field_h + 20]

        screen.fill((20, 20, 20))
        field_surface = pygame.Surface((field_w, field_h))
        road_img = pygame.transform.scale(genera.road_pic, (field_w, field_h))
        field_surface.blit(road_img, (0, road_offset - field_h))
        field_surface.blit(road_img, (0, road_offset))

        # speed lines
        line_surf    = pygame.Surface((field_w, field_h), pygame.SRCALPHA)
        speed_alpha  = min(SPEED_LINE_ALPHA, int(SPEED_LINE_ALPHA * (speed / 15.0)))
        line_spacing = field_h // (SPEED_LINE_COUNT + 1)
        line_len     = min(int(field_h * 0.12 * (speed / 5.0)), int(field_h * 0.25))
        for i in range(1, SPEED_LINE_COUNT + 1):
            y_base = (int(road_offset * 0.6) + i * line_spacing) % field_h
            pygame.draw.line(line_surf, (200, 200, 255, speed_alpha), (4, y_base), (4, y_base + line_len), SPEED_LINE_WIDTH)
            pygame.draw.line(line_surf, (200, 200, 255, speed_alpha), (field_w - 4, y_base), (field_w - 4, y_base + line_len), SPEED_LINE_WIDTH)
        field_surface.blit(line_surf, (0, 0))

        # spawn — genoeg ruimte zodat motor er altijd tussen past op de y-as
        obs_h = int(field_h * OBS_SIZE)
        obs_w = obs_h
        spawn_timer += speed
        if spawn_timer > spawn_distance:
            # safety_margin = 1 motor hoogte + 1 obstacle hoogte + extra marge
            safety_margin = player_h + obs_h + int(field_h * 0.08)
            occupied   = {obs.lane_index for obs in obstacles if obs.y < player_field_y + safety_margin}
            free_lanes = [l for l in range(3) if l not in occupied]
            if len(free_lanes) == 0:
                spawn_timer = spawn_distance * 0.8
            else:
                lane_index          = random.choice(free_lanes)
                obstacle_img        = random.choice([genera.auto_b, genera.auto_g, genera.auto_p, genera.auto_r,
                                                     genera.truck_b, genera.truck_g, genera.truck_p, genera.truck_r])
                obstacle_img_scaled = pygame.transform.scale(obstacle_img, (obs_w, obs_h))
                lane_center_x       = lane_width * lane_index + lane_width // 2
                obs_start_x         = lane_center_x - obs_w // 2
                obstacles.append(Obstacle(lane_index, lane_bounds, obstacle_img_scaled, speed, -obs_h, override_x=obs_start_x))
                spawn_timer = 0

        for obstacle in obstacles:
            obstacle.update()
        obstacles = [o for o in obstacles if not o.is_off_screen(field_h)]

        # obstacle hitboxen
        obs_hitboxes = []
        for obstacle in obstacles:
            r      = obstacle.rect
            hb_w   = int(r.w * OBS_HB_SCALE_X)
            hb_h   = int(r.h * OBS_HB_SCALE_Y)
            obs_hb = pygame.Rect(r.centerx - hb_w // 2, r.centery - hb_h // 2, hb_w, hb_h)
            obs_hitboxes.append((obstacle, obs_hb))

        # draw trail
        if len(trail) >= 2:
            trail_surface = pygame.Surface((field_w, field_h), pygame.SRCALPHA)
            trail_w_px    = max(2, int(player_w * TRAIL_WIDTH))
            for i in range(1, len(trail)):
                t     = i / max(len(trail) - 1, 1)
                alpha = int(t * 210)
                seg_w = max(1, int(trail_w_px * t))
                x1, y1 = int(trail[i - 1][0]), int(trail[i - 1][1])
                x2, y2 = int(trail[i][0]),     int(trail[i][1])
                pygame.draw.line(trail_surface, (*TRAIL_COLOR, alpha // 2), (x1, y1), (x2, y2), max(1, seg_w + 3))
                pygame.draw.line(trail_surface, (*TRAIL_GLOW, alpha),       (x1, y1), (x2, y2), max(1, seg_w))
            field_surface.blit(trail_surface, (0, 0))

        for obstacle, obs_hb in obs_hitboxes:
            field_surface.blit(obstacle.image, (obstacle.x, int(obstacle.y)))

        # player
        hb_w = int(player_w * PLAYER_HB_SCALE_X)
        hb_h = int(player_h * PLAYER_HB_SCALE_Y)
        hitbox_field = pygame.Rect(anchor_x_field - hb_w // 2, player_field_y + (player_h - hb_h) // 2, hb_w, hb_h)

        # lane detection
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
            multiplier       = 1.0
            lane_ticks       = 0
            last_anchor_lane = new_anchor_lane

        # draw player met squish
        squished_w = int(player_w * squish_x)
        squished_h = int(player_h * squish_y)
        motor_img  = pygame.transform.scale(motor_base, (squished_w, squished_h))
        draw_x     = anchor_x_field - squished_w // 2
        draw_y     = player_field_y + (player_h - squished_h) // 2
        field_surface.blit(motor_img, (draw_x, draw_y))

        # collision
        for obstacle, obs_hb in obs_hitboxes:
            if hitbox_field.colliderect(obs_hb):
                running = False
                motor_channel.stop()
                crash_channel.play(crash_sfx)
                last_field_surface = field_surface.copy()
                last_field_x, last_field_y = field_x, field_y
                break

        pygame.draw.rect(field_surface, (60, 60, 60), (0, 0, field_w, field_h), 2)
        screen.blit(field_surface, (field_x, field_y))

        # score + multiplier
        lane_ticks  += 1
        multiplier   = min(MULTIPLIER_BASE * (1 + MULTIPLIER_GROWTH) ** lane_ticks, MULTIPLIER_CAP)
        score       += multiplier * dt * 10

        if int(multiplier) > int(last_multiplier):
            mult_pop_frames_left = MULT_POP_FRAMES
        last_multiplier = multiplier

        if mult_pop_frames_left > 0:
            t_pop     = mult_pop_frames_left / MULT_POP_FRAMES
            font_size = int(28 * (1.0 + (MULT_POP_SCALE - 1.0) * t_pop))
            mult_pop_frames_left -= 1
        else:
            font_size = 28

        font_mult = pygame.font.Font(resource_path("DejaVuSansMono-Bold.ttf"), font_size)
        mult_surf = font_mult.render(f"x{multiplier:.2f}", True, (255, 220, 0))
        screen.blit(mult_surf, mult_surf.get_rect(centerx=field_x + anchor_x_field, bottom=field_y + player_field_y - 4))

        score_surf = font_score.render(f"{int(score)}", True, (255, 255, 255))
        screen.blit(score_surf, (max(8, field_x - score_surf.get_width() - 8), field_y + 8))

        mute_rect = audio.draw_mute_btn(screen)
        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            if mute_rect.collidepoint(event.pos):
                audio.toggle()

        speed += 0.001
        pygame.display.flip()

    audio.unregister_game_sounds()

    # screen shake op het bevroren crash-frame
    if last_field_surface:
        for _ in range(SHAKE_FRAMES):
            ox = random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
            oy = random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
            screen.fill((20, 20, 20))
            screen.blit(last_field_surface, (last_field_x + ox, last_field_y + oy))
            pygame.display.flip()
            clock.tick(60)

    return int(score)