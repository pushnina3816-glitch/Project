import pygame
import math
import random

pygame.init()
pygame.mixer.init()

screen_width = 400
screen_height = 300
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Лягушка")

pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.play(-1)
collision_sound = pygame.mixer.Sound("collision.mp3")
fly_hit_sound = pygame.mixer.Sound("fly_hit.mp3")

x = 200
y = 150
gravity = 2
y_speed = 0
x_speed = 0

projectiles = []
projectile_gravity = 0.5
projectile_power = 12
projectile_angle = 45
on_ground = True

obstacles = []
OBSTACLE_SPAWN_INTERVAL = 120
obstacle_timer = 0

health = 100
flies_shot = 0
MAX_FLIES_TO_WIN = 10
game_state = "playing"
collision_cooldown = 0

frog_image = pygame.image.load("frog.png").convert()
fly_original = pygame.image.load("fly.png").convert_alpha()
fly_image = pygame.transform.scale(fly_original, (15, 10))
obstacle_original = pygame.image.load("stick.png").convert_alpha()
projectile_image = pygame.Surface((10, 10), pygame.SRCALPHA)
pygame.draw.circle(projectile_image, (255, 0, 0), (5, 5), 5)
frog_image.set_colorkey((255, 255, 255))
background_day = pygame.image.load("day1.jpg")
background_night = pygame.image.load("night1.jpg")
background_day = pygame.transform.scale(background_day, (screen_width, screen_height))
background_night = pygame.transform.scale(background_night, (screen_width, screen_height))
frog_image = pygame.transform.scale(frog_image, (40, 40))
background = background_day
flies = []
fly_timer = 0
FLY_SPAWN_INTERVAL = 90
font = pygame.font.Font(None, 24)
big_font = pygame.font.Font(None, 48)
running = True
clock = pygame.time.Clock()

def update_health(change):
    global health
    health += change
    if health > 100:
        health = 100
    elif health < 0:
        health = 0

def draw_health_bar(surface, x, y, width, height, health):
    pygame.draw.rect(surface, (0, 0, 0), (x, y, width, height))
    fill_width = int(width * health / 100)
    if health > 70:
        color = (0, 255, 0)
    elif health > 30:
        color = (255, 255, 0)
    else:
        color = (255, 0, 0)
    pygame.draw.rect(surface, color, (x, y, fill_width, height))
    pygame.draw.rect(surface, (255, 255, 255), (x, y, width, height), 2)

def create_obstacle_with_image(obstacle_width, obstacle_height):
    return pygame.transform.scale(obstacle_original, (obstacle_width, obstacle_height))

while running:
    dt = clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_state == "playing":
                if event.key == pygame.K_w:
                    y_speed = -20
                elif event.key == pygame.K_SPACE:
                    background = background_night if background == background_day else background_day
                elif event.key == pygame.K_a:
                    x_speed = -5
                elif event.key == pygame.K_d:
                    x_speed = 5
                elif event.key == pygame.K_UP:
                    projectile_angle = min(projectile_angle + 5, 80)
                elif event.key == pygame.K_DOWN:
                    projectile_angle = max(projectile_angle - 5, 10)
                elif event.key == pygame.K_LEFT:
                    projectile_power = max(projectile_power - 1, 5)
                elif event.key == pygame.K_RIGHT:
                    projectile_power = min(projectile_power + 1, 25)
                elif event.key == pygame.K_f:
                    rad = math.radians(projectile_angle)
                    projectiles.append([
                        screen_width // 2,
                        y,
                        projectile_power * math.cos(rad),
                        -projectile_power * math.sin(rad),
                        True
                    ])
            elif event.key == pygame.K_r:
                x = 200
                y = 150
                y_speed = 0
                x_speed = 0
                projectiles = []
                obstacles = []
                flies = []
                health = 100
                flies_shot = 0
                game_state = "playing"
                collision_cooldown = 0
                obstacle_timer = 0
                fly_timer = 0
                background = background_day

        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_a, pygame.K_d):
                x_speed = 0

    if game_state == "playing":
        y_speed += gravity
        y += y_speed

        if collision_cooldown > 0:
            collision_cooldown -= 1

        if y + frog_image.get_height() // 2 >= screen_height:
            y = screen_height - frog_image.get_height() // 2
            y_speed = 0
            on_ground = True
        if y - frog_image.get_height() // 2 <= 0:
            y = frog_image.get_height() // 2
            y_speed = 0

        x += x_speed

        bg_x = -x % screen_width
        
        screen.blit(background, (bg_x, 0))
        screen.blit(background, (bg_x - screen_width, 0))

        frog_screen_x = screen_width // 2 - frog_image.get_width() // 2
        frog_screen_y = int(y) - frog_image.get_height() // 2
        
        fly_timer += 1
        if fly_timer >= FLY_SPAWN_INTERVAL:
            fly_timer = 0
            fly_y = random.randint(20, 80)
            if x_speed > 0:
                fly_x = screen_width + 20
                fly_speed = -3
            elif x_speed < 0:
                fly_x = -20
                fly_speed = 3
            else:
                if random.random() < 0.5:
                    fly_x = screen_width + 20
                    fly_speed = -3
                else:
                    fly_x = -20
                    fly_speed = 3
            
            flies.append([fly_x, fly_y, fly_speed])

        new_flies = []
        for fly in flies:
            fly[0] += fly[2]
            
            if -20 <= fly[0] <= screen_width + 20:
                frog_rect = pygame.Rect(frog_screen_x, frog_screen_y, 
                                       frog_image.get_width(), frog_image.get_height())
                fly_rect = pygame.Rect(fly[0] - 7, fly[1] - 5, 15, 10)
                
                if frog_rect.colliderect(fly_rect):
                    update_health(20)
                    flies_shot += 1
                    fly_hit_sound.play()
                    if flies_shot >= MAX_FLIES_TO_WIN:
                        game_state = "win"
                else:
                    screen.blit(fly_image, (fly[0] - 7, fly[1] - 5))
                    new_flies.append(fly)
        
        flies = new_flies

        new_projectiles = []
        for proj in projectiles:
            if proj[4]:
                proj[3] += projectile_gravity
                proj[0] += proj[2]
                proj[1] += proj[3]
                
                if (proj[0] < -10 or proj[0] > screen_width + 10 or 
                    proj[1] < -10 or proj[1] > screen_height + 10):
                    proj[4] = False
                    continue
                
                hit_fly = False
                for fly in flies[:]:
                    fly_rect = pygame.Rect(fly[0] - 7, fly[1] - 5, 15, 10)
                    proj_rect = pygame.Rect(proj[0] - 5, proj[1] - 5, 10, 10)
                    
                    if proj_rect.colliderect(fly_rect):
                        flies.remove(fly)
                        proj[4] = False
                        hit_fly = True
                        update_health(20)
                        flies_shot += 1
                        fly_hit_sound.play()
                        if flies_shot >= MAX_FLIES_TO_WIN:
                            game_state = "win"
                        break
                
                if not hit_fly:
                    screen.blit(projectile_image, (proj[0] - 5, proj[1] - 5))
                    new_projectiles.append(proj)
        
        projectiles = new_projectiles

        obstacle_timer += 1
        if obstacle_timer >= OBSTACLE_SPAWN_INTERVAL:
            obstacle_timer = 0
            obstacle_height = random.randint(15, 35)
            obstacle_width = random.randint(8, 15)
            
            if x_speed > 0:
                obstacle_x = screen_width + 50
            elif x_speed < 0:
                obstacle_x = -50
            else:
                if random.random() < 0.5:
                    obstacle_x = screen_width + 50
                else:
                    obstacle_x = -50
            
            obstacle_img = create_obstacle_with_image(obstacle_width, obstacle_height)
            
            obstacles.append([
                obstacle_x,
                screen_height - obstacle_height,
                obstacle_width,
                obstacle_height,
                x_speed if x_speed != 0 else (3 if obstacle_x > screen_width else -3),
                obstacle_img
            ])

        new_obstacles = []
        for obstacle in obstacles:
            if x_speed != 0:
                obstacle[0] -= x_speed
            else:
                obstacle[0] += obstacle[4]
            
            if -50 <= obstacle[0] <= screen_width + 50:
                screen.blit(obstacle[5], (obstacle[0], obstacle[1]))
                
                if collision_cooldown == 0:
                    frog_rect = pygame.Rect(frog_screen_x, frog_screen_y, 
                                           frog_image.get_width(), frog_image.get_height())
                    obstacle_rect = pygame.Rect(obstacle[0], obstacle[1],
                                               obstacle[2], obstacle[3])
                    
                    if frog_rect.colliderect(obstacle_rect):
                        update_health(-20)
                        collision_sound.play()
                        
                        if health <= 0:
                            game_state = "lose"
                        
                        y_speed = -10
                        collision_cooldown = 30
                
                new_obstacles.append(obstacle)
        
        obstacles = new_obstacles

        screen.blit(frog_image, (frog_screen_x, frog_screen_y))

        if on_ground:
            points = []
            rad = math.radians(projectile_angle)
            temp_vx = projectile_power * math.cos(rad)
            temp_vy = -projectile_power * math.sin(rad)
            temp_x = screen_width // 2
            temp_y = y
            
            for i in range(60):
                temp_vy += projectile_gravity
                temp_x += temp_vx
                temp_y += temp_vy
                
                if temp_y + 5 >= screen_height:
                    break
                    
                points.append((int(temp_x), int(temp_y)))
            
            if len(points) > 1:
                pygame.draw.lines(screen, (255, 255, 255), False, points, 2)

        draw_health_bar(screen, 10, 10, 200, 20, health)
        
        health_text = font.render(f"Здоровье: {health}%", True, (255, 255, 255))
        screen.blit(health_text, (220, 12))
        
        flies_text = font.render(f"Мухи: {flies_shot}/{MAX_FLIES_TO_WIN}", True, (255, 255, 255))
        screen.blit(flies_text, (10, 40))
        
        angle_text = font.render(f"Угол: {projectile_angle}°", True, (255, 255, 255))
        power_text = font.render(f"Сила: {projectile_power}", True, (255, 255, 255))
        
        screen.blit(angle_text, (10, 65))
        screen.blit(power_text, (10, 90))
    
    elif game_state == "win":
        win_bg = pygame.Surface((screen_width, screen_height))
        win_bg.fill((0, 100, 0))
        screen.blit(win_bg, (0, 0))
        
        win_text = big_font.render("ПОБЕДА!", True, (255, 255, 0))
        screen.blit(win_text, (screen_width // 2 - win_text.get_width() // 2, 
                              screen_height // 2 - 50))
        
        details_text = font.render(f"Вы сбили {flies_shot} мух!", True, (255, 255, 255))
        screen.blit(details_text, (screen_width // 2 - details_text.get_width() // 2, 
                                  screen_height // 2))
        
        restart_text = font.render("Нажмите R для новой игры", True, (255, 255, 255))
        screen.blit(restart_text, (screen_width // 2 - restart_text.get_width() // 2, 
                                  screen_height // 2 + 50))
        
        screen.blit(frog_image, (screen_width // 2 - frog_image.get_width() // 2,
                                screen_height // 2 + 100))
        
        for i in range(10):
            angle = i * 36 * 3.14 / 180
            fly_x = screen_width // 2 + int(80 * math.cos(angle))
            fly_y = screen_height // 2 + 100 + int(80 * math.sin(angle))
            screen.blit(fly_image, (fly_x - 7, fly_y - 5))
    
    elif game_state == "lose":
        lose_bg = pygame.Surface((screen_width, screen_height))
        lose_bg.fill((100, 0, 0))
        screen.blit(lose_bg, (0, 0))
        
        lose_text = big_font.render("ПРОИГРЫШ!", True, (255, 0, 0))
        screen.blit(lose_text, (screen_width // 2 - lose_text.get_width() // 2, 
                               screen_height // 2 - 50))
        
        details_text = font.render(f"Вы сбили {flies_shot} мух", True, (255, 255, 255))
        screen.blit(details_text, (screen_width // 2 - details_text.get_width() // 2, 
                                  screen_height // 2))
        
        reason_text = font.render("Здоровье лягушки закончилось", True, (255, 255, 255))
        screen.blit(reason_text, (screen_width // 2 - reason_text.get_width() // 2, 
                                 screen_height // 2 + 30))
        
        restart_text = font.render("Нажмите R для новой игры", True, (255, 255, 255))
        screen.blit(restart_text, (screen_width // 2 - restart_text.get_width() // 2, 
                                  screen_height // 2 + 70))
        
        sad_frog = frog_image.copy()
        frog_pixels = pygame.PixelArray(sad_frog)
        frog_pixels.replace((50, 205, 50), (200, 50, 50))
        del frog_pixels
        screen.blit(sad_frog, (screen_width // 2 - sad_frog.get_width() // 2,
                               screen_height // 2 + 120))

    pygame.display.flip()

pygame.mixer.music.stop()
pygame.quit()