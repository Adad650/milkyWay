import pygame, sys, random, math, time

pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Echo.")
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 40)

white = (255, 255, 255)
black = (0, 0, 0)
gray = (80, 80, 80)
blue = (0, 100, 255)
lBlue = (0, 150, 255)

playerPNG = pygame.image.load("player.png").convert_alpha()
playerPNG = pygame.transform.scale(playerPNG, (40, 40))

state = "cutscene1"

# --- Cutscene helpers ---
def fade_in(duration=1000):
    fade = pygame.Surface((800, 600))
    for alpha in range(255, -1, -15):
        fade.set_alpha(alpha)
        screen.fill(black)
        pygame.draw.rect(screen, gray, (0, 440, 800, 40))
        screen.blit(fade, (0, 0))
        pygame.display.flip()
        clock.tick(30)
        pygame.time.delay(duration // 20)

def fade_out(duration=1000):
    fade = pygame.Surface((800, 600))
    for alpha in range(0, 255, 15):
        fade.set_alpha(alpha)
        screen.blit(fade, (0, 0))
        pygame.display.flip()
        clock.tick(30)
        pygame.time.delay(duration // 20)

# --- Cutscene 1: Conveyor Belt ---
def cutscene1():
    global state
    robots = [pygame.Rect(800 + i * 120, 400, 40, 40) for i in range(6)]
    belt_speed = 2
    text1 = small_font.render("Worker 1: We ran out of cameras!", True, white)
    text2 = small_font.render("Worker 2: Just give him an extra speaker!", True, white)
    start_time = pygame.time.get_ticks()
    fade_in(800)
    while pygame.time.get_ticks() - start_time < 6000:
        screen.fill((10, 10, 10))
        pygame.draw.rect(screen, gray, (0, 440, 800, 40))

        # Belt lights
        for i in range(0, 800, 60):
            pygame.draw.circle(screen, (30, 30, 30), (i + (pygame.time.get_ticks()//100) % 60, 460), 6)

        # Robots move left
        for r in robots:
            r.x -= belt_speed
            if r.right < 0:
                r.x = 800
            screen.blit(playerPNG, r)

        # Dialogue
        elapsed = pygame.time.get_ticks() - start_time
        if elapsed < 3000:
            screen.blit(text1, (160, 100))
        else:
            screen.blit(text2, (140, 150))

        pygame.display.flip()
        clock.tick(60)
    fade_out(600)
    state = "cutscene2"

# --- Cutscene 2: Robot Awakens ---
def cutscene2():
    global state
    start_time = pygame.time.get_ticks()
    pos = [400, 300]
    light_radius = 80
    fade_in(600)
    while pygame.time.get_ticks() - start_time < 4000:
        screen.fill((0, 0, 0))
        pos[0] += random.choice([-2, 2])
        pos[1] += random.choice([-2, 2])
        rect = playerPNG.get_rect(center=pos)
        screen.blit(playerPNG, rect)

        # Pulsing light to simulate “echolocation starting”
        light_radius = 80 + int(20 * math.sin(pygame.time.get_ticks() / 200))
        light = pygame.Surface((800, 600), pygame.SRCALPHA)
        pygame.draw.circle(light, (255, 255, 255, 60), rect.center, light_radius)
        screen.blit(light, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        text = small_font.render("Where... am I?", True, white)
        screen.blit(text, (320, 100))
        pygame.display.flip()
        clock.tick(30)
    fade_out(600)
    state = "tutorial"

# --- Tutorial message display ---
def tutorial():
    global state
    start_time = pygame.time.get_ticks()
    fade_in(400)
    while True:
        screen.fill(black)
        elapsed = pygame.time.get_ticks() - start_time
        if elapsed < 4000:
            screen.blit(small_font.render("Click to emit sound (your echo).", True, white), (140, 200))
        elif elapsed < 8000:
            screen.blit(small_font.render("Use W A S D to move.", True, white), (220, 250))
        elif elapsed < 12000:
            screen.blit(small_font.render("Find your way to the exit...", True, white), (180, 300))
        else:
            fade_out(400)
            state = "game"
            break
        pygame.display.flip()
        clock.tick(30)

# --- Maze Generation ---
def genMaze(width, height):
    random.seed(time.time())
    maze = [[1 for _ in range(width)] for _ in range(height)]
    directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    def carve(x, y):
        maze[y][x] = 0
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = (x + dx * 2), (y + dy * 2)
            if 0 <= ny < height and 0 <= nx < width and maze[ny][nx] == 1:
                maze[y + dy][x + dx] = 0
                carve(nx, ny)
    carve(0, 0)
    maze[0][0] = 0
    maze[height - 1][width - 1] = 0
    return maze

cellSize = 40
mazeX, mazeY = 31, 21
maze = genMaze(mazeX, mazeY)
screenWidth, screenHeight = mazeX * cellSize, mazeY * cellSize
screen = pygame.display.set_mode((screenWidth, screenHeight))

wallColor = (0, 0, 80)
exitColor = (0, 255, 0)

player = playerPNG.get_rect(center=(10, 10))
exit_rect = pygame.Rect((mazeX - 1) * cellSize, (mazeY - 1) * cellSize, cellSize, cellSize)
walls = [pygame.Rect(x * cellSize, y * cellSize, cellSize, cellSize)
         for y in range(mazeY) for x in range(mazeX) if maze[y][x] == 1]
echoes = []
level = 1
echCooldown = 2000
lastEchoTime = 0
cooldownMsg = ""
coolDownMsgTimer = 0

# --- Movement ---
def move_player(rect, dx, dy, walls):
    rect.x += dx
    for wall in walls:
        if rect.colliderect(wall):
            if dx > 0: rect.right = wall.left
            elif dx < 0: rect.left = wall.right
    rect.y += dy
    for wall in walls:
        if rect.colliderect(wall):
            if dy > 0: rect.bottom = wall.top
            elif dy < 0: rect.top = wall.bottom

# --- MAIN LOOP ---
run = True
while run:
    if state == "cutscene1":
        cutscene1()
    elif state == "cutscene2":
        cutscene2()
    elif state == "tutorial":
        tutorial()
    elif state == "game":
        # normal gameplay
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                currentTime = pygame.time.get_ticks()
                if currentTime - lastEchoTime >= echCooldown:
                    echoes.append([player.centerx, player.centery, 0, 255])
                    lastEchoTime = currentTime
                    cooldownMsg = ""
                else:
                    cooldownMsg = "Echo On Cooldown"
                    coolDownMsgTimer = currentTime

        key = pygame.key.get_pressed()
        speed = 4 if (key[pygame.K_LSHIFT] or key[pygame.K_RSHIFT]) else 2
        dx, dy = 0, 0
        if key[pygame.K_w]: dy = -speed
        if key[pygame.K_s]: dy = speed
        if key[pygame.K_a]: dx = -speed
        if key[pygame.K_d]: dx = speed
        move_player(player, dx, dy, walls)

        # draw maze
        screen.fill((0, 0, 0))
        for y in range(mazeY):
            for x in range(mazeX):
                rect = pygame.Rect(x * cellSize, y * cellSize, cellSize, cellSize)
                if y == mazeY - 1 and x == mazeX - 1:
                    pygame.draw.rect(screen, exitColor, rect)
                elif maze[y][x] == 1:
                    pygame.draw.rect(screen, wallColor, rect)
        screen.blit(playerPNG, player)

        # darkness + echo
        darkness = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
        darkness.fill((0, 0, 0, 255))
        for echo in echoes[:]:
            ex, ey, r, a = echo
            r += 8
            a -= 5
            echo[2], echo[3] = r, a
            if a <= 0:
                echoes.remove(echo)
                continue
            for y in range(mazeY):
                for x in range(mazeX):
                    cx, cy = x * cellSize + cellSize // 2, y * cellSize + cellSize // 2
                    dist = math.hypot(cx - ex, cy - ey)
                    if dist < r:
                        rect = pygame.Rect(x * cellSize, y * cellSize, cellSize, cellSize)
                        if maze[y][x] == 1:
                            pygame.draw.rect(darkness, (0, 0, 0, 100), rect)
                        else:
                            pygame.draw.rect(darkness, (0, 0, 0, 0), rect)
        screen.blit(darkness, (0, 0))
        screen.blit(playerPNG, player)

        # cooldown text
        currentTime = pygame.time.get_ticks()
        if cooldownMsg != "" and currentTime - coolDownMsgTimer < 1000:
            smallText = small_font.render(cooldownMsg, True, (255, 50, 50))
            rect = smallText.get_rect(center=(400, 500))
            screen.blit(smallText, rect)
            barWidth = 300
            barHeight = 15
            barX = (screenWidth - barWidth) // 2
            barY = screenHeight - 40
            
            timeSinceEcho = currentTime - lastEchoTime
            progress = min(timeSinceEcho / echCooldown, 1.0)

            pygame.draw.rect(screen, (50, 50, 50), (barX, barY, barWidth, barHeight))

            pygame.draw.rect(screen, (0, 150, 255), (barX, barY, barWidth * progress, barHeight))

            pygame.draw.rect(screen, white, (barX, barY, barWidth, barHeight), 2)

            label = small_font.render("Echo Cooldown", True, white)
            screen.blit(label, (barX + 70, barY - 25))



        level_text = small_font.render(f"Level {level}", True, white)
        screen.blit(level_text, (400, 10))

        # exit reached
        if player.colliderect(exit_rect):
            screen.fill(black)
            goal_text = small_font.render("Goal: Get him a camera!", True, white)
            screen.blit(goal_text, (screenWidth // 2 - 200, screenHeight // 2 + 80))
            message = font.render("Good Job!", True, (0, 255, 0))
            sub_message = small_font.render(f"Level {level} Complete", True, white)
            screen.blit(message, (screenWidth // 2 - 150, screenHeight // 2 - 50))
            screen.blit(sub_message, (screenWidth // 2 - 130, screenHeight // 2 + 20))
            pygame.display.flip()
            pygame.time.delay(1500)
            level += 1
            echCooldown = max(500, 2000 - level * 100)
            maze = genMaze(mazeX, mazeY)
            walls = [pygame.Rect(x * cellSize, y * cellSize, cellSize, cellSize)
                     for y in range(mazeY) for x in range(mazeX) if maze[y][x] == 1]
            exit_rect = pygame.Rect((mazeX - 1) * cellSize, (mazeY - 1) * cellSize, cellSize, cellSize)
            echoes.clear()
            player.x, player.y = 0, 0

        pygame.display.flip()
        player.clamp_ip(screen.get_rect())
        clock.tick(60)

pygame.quit()
sys.exit()
