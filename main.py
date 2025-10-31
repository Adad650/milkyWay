import pygame, sys, random, math, time

pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Echo.")
font = pygame.font.Font(None, 74)

white = (255, 255, 255)
black = (0, 0, 0)
lBlue = (0, 150, 255)
blue = (0, 100, 255)

echCooldown = 2000
lastEchoTime = 0
cooldownMsg = ""
coolDownMsgTimer = 0
smallText = ""
small_font = pygame.font.Font(None, 50)
level = 1

run = False
menu = True

while menu:
    screen.fill(black)
    text = font.render("Echo.", True, white)
    text_rect = text.get_rect(center=(400, 150))
    screen.blit(text, text_rect)
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    play_rect = pygame.Rect(300, 250, 200, 70)
    if play_rect.collidepoint(mouse):
        pygame.draw.rect(screen, lBlue, play_rect)
        if click[0] == 1:
            run = True
            menu = False
    else:
        pygame.draw.rect(screen, blue, play_rect)
    play_text = small_font.render("Play", True, white)
    screen.blit(play_text, (play_rect.x + 65, play_rect.y + 15))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            menu = False
    pygame.display.flip()


playerPNG = pygame.image.load("player.png").convert_alpha()
playerPNG = pygame.transform.scale(playerPNG, (40, 40))
player = playerPNG.get_rect(center=(10, 10))
echoes = []

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
pygame.display.set_caption("Echo.")

wallColor = (0, 0, 80)
pathColor = (0, 0, 0)
exitColor = (0, 255, 0)

exit_rect = pygame.Rect((mazeX - 1) * cellSize, (mazeY - 1) * cellSize, cellSize, cellSize)

def move_player(rect, dx, dy, walls):
    rect.x += dx
    for wall in walls:
        if rect.colliderect(wall):
            if dx > 0:
                rect.right = wall.left
            elif dx < 0:
                rect.left = wall.right
    rect.y += dy
    for wall in walls:
        if rect.colliderect(wall):
            if dy > 0:
                rect.bottom = wall.top
            elif dy < 0:
                rect.top = wall.bottom

walls = [pygame.Rect(x * cellSize, y * cellSize, cellSize, cellSize) for y in range(mazeY) for x in range(mazeX) if maze[y][x] == 1]

run = True

while run:
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
    if key[pygame.K_w]:
        dy = -speed
    if key[pygame.K_s]:
        dy = speed
    if key[pygame.K_a]:
        dx = -speed
    if key[pygame.K_d]:
        dx = speed
    move_player(player, dx, dy, walls)

    screen.fill((0, 0, 0))
    for y in range(mazeY):
        for x in range(mazeX):
            rect = pygame.Rect(x * cellSize, y * cellSize, cellSize, cellSize)
            if y == mazeY - 1 and x == mazeX - 1:
                pygame.draw.rect(screen, exitColor, rect)
            elif maze[y][x] == 1:
                pygame.draw.rect(screen, wallColor, rect)
    screen.blit(playerPNG, player)

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
        pygame.draw.circle(darkness, (0, 0, 0, 0), (ex, ey), r)
    screen.blit(darkness, (0, 0))
    screen.blit(playerPNG, player)

    currentTime = pygame.time.get_ticks()
    if cooldownMsg != "" and currentTime - coolDownMsgTimer < 1000:
        smallText = small_font.render(cooldownMsg, True, (255, 50, 50))
        rect = smallText.get_rect(center=(400, 500))
        screen.blit(smallText, rect)

    level_text = small_font.render(f"Level {level}", True, white)
    screen.blit(level_text, (400, 10))

    if player.colliderect(exit_rect):
        screen.fill(black)
        message = font.render("Good Job!", True, (0, 255, 0))
        sub_message = small_font.render(f"Level {level} Complete", True, white)
        screen.blit(message, (screenWidth // 2 - 150, screenHeight // 2 - 50))
        screen.blit(sub_message, (screenWidth // 2 - 130, screenHeight // 2 + 20))
        pygame.display.flip()
        pygame.time.delay(1500)
        level += 1
        echCooldown = 2000 - level * 100
        if echCooldown < 500:
            echCooldown = 500
        maze = genMaze(mazeX, mazeY)
        walls = [pygame.Rect(x * cellSize, y * cellSize, cellSize, cellSize) for y in range(mazeY) for x in range(mazeX) if maze[y][x] == 1]
        exit_rect = pygame.Rect((mazeX - 1) * cellSize, (mazeY - 1) * cellSize, cellSize, cellSize)
        echoes.clear()
        player.x, player.y = 0, 0
        screen.fill((0, 0, 0))
        pygame.display.flip()
        pygame.time.delay(300)

    pygame.display.flip()
    player.clamp_ip(screen.get_rect())
    clock.tick(60)

pygame.quit()
sys.exit()
