import pygame
import random
import math
import time
import sys

pygame.init()
clock = pygame.time.Clock()

cellSize = 40
mazeWide = 31
mazeTall = 21
screenWide = cellSize * mazeWide
screenTall = cellSize * mazeTall

whiteColor = (255, 255, 255)
blackColor = (0, 0, 0)
spaceColor = (15, 15, 28)
exitLockedColor = (255, 70, 70)
exitOpenColor = (80, 255, 150)
keyColor = (255, 220, 0)
buttonColor = (70, 200, 255)
buttonDoneColor = (0, 180, 180)
buddyColor = (255, 140, 200)
wallColors = [(90, 0, 180), (0, 140, 200), (200, 80, 30), (120, 160, 60)]
floorColors = [(20, 20, 40), (18, 28, 52), (26, 16, 48)]
currentWallColor = wallColors[0]
currentFloorColor = floorColors[0]

screen = pygame.display.set_mode((screenWide, screenTall))
pygame.display.set_caption("Echo Maze Remix")

bigFont = pygame.font.Font(None, 72)
mediumFont = pygame.font.Font(None, 46)
miniFont = pygame.font.Font(None, 32)

playerPic = pygame.transform.scale(pygame.image.load("player.png").convert_alpha(), (40, 40))

gameState = "cutscene1"
mazeMap = []
mazeWalls = []
playerHitboxSize = 26
playerBox = pygame.Rect(0, 0, playerHitboxSize, playerHitboxSize)
exitBox = pygame.Rect((mazeWide - 1) * cellSize, (mazeTall - 1) * cellSize, cellSize, cellSize)
puzzlesNow = []
exitLocked = True
unlockFlashTime = 0

echoBalls = []
echoDelay = 2000
lastEchoTime = 0
cooldownWords = ""
cooldownTime = 0

levelNumber = 1
levelStartTick = 0
levelLine = ""
lineTimer = 0

tutorialLevelActive = False
tutorialLines = []

gameStarted = False

buddySayings = [
    "Please don't bump walls.",
    "This place echoes weird!",
    "Let me ride on your head!",
    "We should make a club."
]

levelNotes = [
    "Maze tip: corners hide secrets.",
    "Echo more, worry less.",
    "Shift = sprint. use it!",
    "Keys do not eat batteries.",
    "Floor buttons love attention.",
    "If it's shiny, touch it.",
    "Left click blasts sound. do it a lot!"
]

victoryBlurbs = [
    "Camera quest marches on!",
    "The boss owes you snacks.",
    "Echo hero status increasing.",
    "More puzzles await..."
]


def fadeIn(ms=800):
    w, h = screen.get_size()
    cover = pygame.Surface((w, h))
    for alpha in range(255, -1, -20):
        cover.set_alpha(alpha)
        screen.fill(blackColor)
        screen.blit(cover, (0, 0))
        pygame.display.flip()
        pygame.time.delay(max(1, ms // 20))


def fadeOut(ms=800):
    w, h = screen.get_size()
    cover = pygame.Surface((w, h))
    for alpha in range(0, 256, 20):
        cover.set_alpha(alpha)
        screen.blit(cover, (0, 0))
        pygame.display.flip()
        pygame.time.delay(max(1, ms // 20))


def sceneOne():
    global gameState
    beltY = screenTall - 200
    robots = [pygame.Rect(screenWide + i * 115, beltY - 40, 40, 40) for i in range(6)]
    fadeIn(700)
    start = pygame.time.get_ticks()
    beltSpeed = 2
    textOne = miniFont.render("Worker 1: We ran out of cameras!", True, whiteColor)
    textTwo = miniFont.render("Worker 2: Just give him extra speakers!", True, whiteColor)
    while pygame.time.get_ticks() - start < 6000:
        screen.fill(spaceColor)
        pygame.draw.rect(screen, (40, 40, 40), (0, beltY, screenWide, 40))
        lampShift = (pygame.time.get_ticks() // 120) % 60
        for i in range(0, screenWide, 60):
            pygame.draw.circle(screen, (80, 80, 80), (i + lampShift, beltY + 20), 6)
        for robo in robots:
            robo.x -= beltSpeed
            if robo.right < 0:
                robo.x = screenWide
            screen.blit(playerPic, robo)
        if pygame.time.get_ticks() - start < 3200:
            screen.blit(textOne, ((screenWide - textOne.get_width()) // 2, screenTall // 3))
        else:
            screen.blit(textTwo, ((screenWide - textTwo.get_width()) // 2, screenTall // 3 + 60))
        pygame.display.flip()
        clock.tick(60)
    fadeOut(500)
    gameState = "cutscene2"


def sceneTwo():
    global gameState
    fadeIn(500)
    start = pygame.time.get_ticks()
    spot = [float(screenWide // 2), float(screenTall // 2)]
    calmText = mediumFont.render("Anybody out there?", True, whiteColor)
    quietText = mediumFont.render("It's really quiet...", True, whiteColor)
    while pygame.time.get_ticks() - start < 4000:
        screen.fill((8, 8, 14))
        wiggleA = math.sin(pygame.time.get_ticks() / 600) * 1.5
        wiggleB = math.cos(pygame.time.get_ticks() / 900) * 1.4
        spot[0] += wiggleA * 0.2
        spot[1] += wiggleB * 0.2
        botRect = playerPic.get_rect(center=(int(spot[0]), int(spot[1])))
        screen.blit(playerPic, botRect)
        glow = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        glowSize = 90 + int(6 * math.sin(pygame.time.get_ticks() / 400))
        pygame.draw.circle(glow, (200, 200, 255, 90), botRect.center, glowSize)
        screen.blit(glow, (0, 0))
        screen.blit(calmText, ((screenWide - calmText.get_width()) // 2, screenTall // 3))
        if pygame.time.get_ticks() % 1100 > 550:
            screen.blit(quietText, ((screenWide - quietText.get_width()) // 2, screenTall // 3 + 50))
        pygame.display.flip()
        clock.tick(30)
    fadeOut(400)
    gameState = "tutorial"


def showTutorial():
    global gameState
    fadeIn(400)
    start = pygame.time.get_ticks()
    tipOne = mediumFont.render("Click to blast sound (it's your echo)!", True, whiteColor)
    tipTwo = mediumFont.render("Use W A S D to move. Shift makes you zoomy.", True, whiteColor)
    tipThree = mediumFont.render("The exit likes puzzles now. Finish what it wants.", True, whiteColor)
    tipFour = mediumFont.render("Keys, floor buttons, tiny bots... all random.", True, whiteColor)
    while True:
        screen.fill(blackColor)
        t = pygame.time.get_ticks() - start
        if t < 4000:
            screen.blit(tipOne, ((screenWide - tipOne.get_width()) // 2, screenTall // 2 - 80))
        elif t < 8000:
            screen.blit(tipTwo, ((screenWide - tipTwo.get_width()) // 2, screenTall // 2 - 20))
        elif t < 12000:
            screen.blit(tipThree, ((screenWide - tipThree.get_width()) // 2, screenTall // 2 + 40))
        elif t < 16000:
            screen.blit(tipFour, ((screenWide - tipFour.get_width()) // 2, screenTall // 2 + 100))
        else:
            break
        pygame.display.flip()
        clock.tick(30)
    fadeOut(400)
    gameState = "game"


def makeMaze(w, h):
    random.seed(time.time())
    grid = [[1 for _ in range(w)] for _ in range(h)]
    def carve(cx, cy):
        grid[cy][cx] = 0
        dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx = cx + dx * 2
            ny = cy + dy * 2
            if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] == 1:
                grid[cy + dy][cx + dx] = 0
                carve(nx, ny)
    carve(0, 0)
    grid[0][0] = 0
    grid[h - 1][w - 1] = 0
    return grid


def getOpenSpots(grid):
    spots = []
    for ty in range(mazeTall):
        for tx in range(mazeWide):
            if grid[ty][tx] == 0 and (tx, ty) not in [(0, 0), (mazeWide - 1, mazeTall - 1)]:
                spots.append((tx, ty))
    return spots


def takeSpot(spots):
    if not spots:
        return random.randint(0, mazeWide - 1), random.randint(0, mazeTall - 1)
    idx = random.randrange(len(spots))
    return spots.pop(idx)


def buildPuzzle(kind, level, spots):
    if kind == "keys":
        total = min(3 + level // 2, 6)
        boxes = []
        for _ in range(total):
            x, y = takeSpot(spots)
            boxes.append(pygame.Rect(x * cellSize + 10, y * cellSize + 10, cellSize - 20, cellSize - 20))
        return {"type": "keys", "rects": boxes, "need": total, "grabbed": 0, "flash": 0}
    if kind == "buttons":
        total = min(2 + level // 3, 5)
        pads = []
        for _ in range(total):
            x, y = takeSpot(spots)
            pads.append({"rect": pygame.Rect(x * cellSize + 8, y * cellSize + 8, cellSize - 16, cellSize - 16),
                         "done": False,
                         "flash": 0})
        return {"type": "buttons", "pads": pads}
    if kind == "buddy":
        x, y = takeSpot(spots)
        buddyRect = pygame.Rect(x * cellSize + 6, y * cellSize + 6, cellSize - 12, cellSize - 12)
        return {"type": "buddy",
                "rect": buddyRect,
                "found": False,
                "follow": [float(buddyRect.centerx), float(buddyRect.centery)],
                "chat": 0,
                "line": random.choice(buddySayings)}
    return {"type": "none"}


def makePuzzles(level, grid):
    spots = getOpenSpots(grid)
    random.shuffle(spots)
    kinds = ["keys", "buttons", "buddy"]
    random.shuffle(kinds)
    count = 1
    if level >= 2:
        count = 2
    if level >= 4:
        count = 3
    picked = kinds[:count]
    puzzles = []
    for k in picked:
        puzzles.append(buildPuzzle(k, level, spots))
    return puzzles


def startLevel():
    global mazeMap, mazeWalls, exitBox, playerBox, puzzlesNow, exitLocked, unlockFlashTime
    global levelStartTick, levelLine, lineTimer, gameStarted, screen, cooldownWords, cooldownTime, lastEchoTime
    global currentWallColor, currentFloorColor, tutorialLevelActive, tutorialLines
    if screen.get_size() != (screenWide, screenTall):
        screen = pygame.display.set_mode((screenWide, screenTall))
    mazeMap.clear()
    mazeMap.extend(makeMaze(mazeWide, mazeTall))
    mazeWalls.clear()
    for my in range(mazeTall):
        for mx in range(mazeWide):
            if mazeMap[my][mx] == 1:
                mazeWalls.append(pygame.Rect(mx * cellSize, my * cellSize, cellSize, cellSize))
    exitBox = pygame.Rect((mazeWide - 1) * cellSize, (mazeTall - 1) * cellSize, cellSize, cellSize)
    playerBox.width = playerHitboxSize
    playerBox.height = playerHitboxSize
    playerBox.center = (cellSize // 2, cellSize // 2)
    puzzlesNow.clear()
    tutorialLevelActive = (levelNumber == 1)
    if tutorialLevelActive:
        exitLocked = False
        tutorialLines = [
            "Tutorial Level!",
            "Move with W A S D or the arrow keys.",
            "Hold shift to sprint when you need speed.",
            "Left click to shout your echo pulse.",
            "Walk into the green exit to keep going."
        ]
    else:
        puzzlesNow.extend(makePuzzles(levelNumber, mazeMap))
        exitLocked = True if puzzlesNow else False
        tutorialLines = []
    unlockFlashTime = 0
    levelStartTick = pygame.time.get_ticks()
    levelLine = "" if tutorialLevelActive else random.choice(levelNotes)
    lineTimer = levelStartTick
    gameStarted = True
    cooldownWords = ""
    cooldownTime = levelStartTick
    lastEchoTime = levelStartTick - echoDelay
    echoBalls.clear()
    currentWallColor = random.choice(wallColors)
    currentFloorColor = random.choice(floorColors)
    if tutorialLevelActive:
        print("level", levelNumber, "tutorial level active")
    else:
        print("level", levelNumber, "puzzles:", [p["type"] for p in puzzlesNow])


def updatePuzzles():
    doneEverything = True
    now = pygame.time.get_ticks()
    for stuff in puzzlesNow:
        if stuff["type"] == "keys":
            for box in stuff["rects"][:]:
                if playerBox.colliderect(box):
                    stuff["rects"].remove(box)
                    stuff["grabbed"] += 1
                    stuff["flash"] = now
            if stuff["rects"]:
                doneEverything = False
        elif stuff["type"] == "buttons":
            for pad in stuff["pads"]:
                if playerBox.colliderect(pad["rect"]):
                    if not pad["done"]:
                        pad["done"] = True
                        pad["flash"] = now
            if any(not pad["done"] for pad in stuff["pads"]):
                doneEverything = False
        elif stuff["type"] == "buddy":
            if not stuff["found"] and playerBox.colliderect(stuff["rect"]):
                stuff["found"] = True
                stuff["chat"] = now
                stuff["follow"][0] = float(stuff["rect"].centerx)
                stuff["follow"][1] = float(stuff["rect"].centery)
            if stuff["found"]:
                px, py = playerBox.center
                stuff["follow"][0] += (px - stuff["follow"][0]) * 0.12
                stuff["follow"][1] += (py - stuff["follow"][1]) * 0.12
                stuff["rect"].center = (int(stuff["follow"][0]), int(stuff["follow"][1]))
            else:
                doneEverything = False
    return doneEverything


def drawPuzzles():
    now = pygame.time.get_ticks()
    for stuff in puzzlesNow:
        if stuff["type"] == "keys":
            for box in stuff["rects"]:
                pygame.draw.rect(screen, keyColor, box)
                pygame.draw.rect(screen, blackColor, box, 2)
        elif stuff["type"] == "buttons":
            for pad in stuff["pads"]:
                col = buttonDoneColor if pad["done"] else buttonColor
                pygame.draw.rect(screen, col, pad["rect"])
                pygame.draw.rect(screen, blackColor, pad["rect"], 2)
        elif stuff["type"] == "buddy":
            col = buddyColor if stuff["found"] else (200, 100, 255)
            pygame.draw.rect(screen, col, stuff["rect"])
            pygame.draw.rect(screen, blackColor, stuff["rect"], 2)
            if stuff["found"] and now - stuff["chat"] < 2600:
                bubble = miniFont.render(stuff["line"], True, whiteColor)
                bubbleRect = bubble.get_rect(center=(stuff["rect"].centerx, stuff["rect"].top - 20))
                screen.blit(bubble, bubbleRect)


def puzzleMessages():
    if tutorialLevelActive:
        return []
    words = []
    for stuff in puzzlesNow:
        if stuff["type"] == "keys":
            left = len(stuff["rects"])
            words.append(f"Keys grabbed {stuff['grabbed']} / {stuff['need']} (need {left} more)")
        elif stuff["type"] == "buttons":
            lit = sum(1 for pad in stuff["pads"] if pad["done"])
            words.append(f"Floor buttons lit {lit} / {len(stuff['pads'])}")
        elif stuff["type"] == "buddy":
            if stuff["found"]:
                words.append("Tiny bot found! get to the exit together.")
            else:
                words.append("Find the tiny bot hiding in the maze.")
    if not words:
        words.append("Exit is open. just go!")
    return words


def pushPlayer(rect, dx, dy):
    rect.x += dx
    for wall in mazeWalls:
        if rect.colliderect(wall):
            if dx > 0:
                rect.right = wall.left
            elif dx < 0:
                rect.left = wall.right
    rect.y += dy
    for wall in mazeWalls:
        if rect.colliderect(wall):
            if dy > 0:
                rect.bottom = wall.top
            elif dy < 0:
                rect.top = wall.bottom
    return rect


def drawMaze():
    for my in range(mazeTall):
        for mx in range(mazeWide):
            tile = pygame.Rect(mx * cellSize, my * cellSize, cellSize, cellSize)
            if my == mazeTall - 1 and mx == mazeWide - 1:
                color = exitLockedColor if exitLocked else exitOpenColor
                pygame.draw.rect(screen, color, tile)
            elif mazeMap[my][mx] == 1:
                pygame.draw.rect(screen, currentWallColor, tile)
            else:
                if (mx + my) % 2 == 0:
                    pygame.draw.rect(screen, currentFloorColor, tile)


def runEchoes():
    dark = pygame.Surface((screenWide, screenTall), pygame.SRCALPHA)
    dark.fill((0, 0, 0, 255))
    for wave in echoBalls[:]:
        wave[2] += 8
        wave[3] -= 5
        if wave[3] <= 0:
            echoBalls.remove(wave)
            continue
        for my in range(mazeTall):
            for mx in range(mazeWide):
                cx = mx * cellSize + cellSize // 2
                cy = my * cellSize + cellSize // 2
                dist = math.hypot(cx - wave[0], cy - wave[1])
                if dist < wave[2]:
                    block = pygame.Rect(mx * cellSize, my * cellSize, cellSize, cellSize)
                    if mazeMap[my][mx] == 1:
                        dark.fill((0, 0, 0, 120), block)
                    else:
                        dark.fill((0, 0, 0, 0), block)
    screen.blit(dark, (0, 0))


def drawPlayer():
    sprite_rect = playerPic.get_rect(center=playerBox.center)
    screen.blit(playerPic, sprite_rect)


runGame = True
while runGame:
    if gameState == "cutscene1":
        sceneOne()
    elif gameState == "cutscene2":
        sceneTwo()
    elif gameState == "tutorial":
        showTutorial()
    elif gameState == "game":
        if not gameStarted:
            startLevel()
        dt = clock.get_time() / 16.67
        if dt <= 0:
            dt = 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                runGame = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                now = pygame.time.get_ticks()
                if now - lastEchoTime >= echoDelay:
                    echoBalls.append([playerBox.centerx, playerBox.centery, 0, 255])
                    lastEchoTime = now
                    cooldownWords = ""
                else:
                    cooldownWords = "Echo is cooling down!"
                    cooldownTime = now
        keys = pygame.key.get_pressed()
        moveX = 0
        moveY = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            moveY -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            moveY += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            moveX -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            moveX += 1
        if moveX != 0 and moveY != 0:
            moveX *= 0.7071
            moveY *= 0.7071
        speed = 3.2 * dt
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            speed = 5.0 * dt
        playerBox = pushPlayer(playerBox, int(moveX * speed), int(moveY * speed))
        playerBox.clamp_ip(screen.get_rect())

        wasLocked = exitLocked
        allDone = updatePuzzles()
        exitLocked = not allDone
        if wasLocked and not exitLocked:
            unlockFlashTime = pygame.time.get_ticks()
            levelLine = "EXIT IS OPEN!!!"
            lineTimer = unlockFlashTime

        nowTime = pygame.time.get_ticks()
        if not tutorialLevelActive and nowTime - lineTimer > 7000:
            levelLine = random.choice(levelNotes)
            lineTimer = nowTime

        screen.fill(spaceColor)
        drawMaze()
        drawPlayer()
        runEchoes()
        drawPuzzles()
        if tutorialLevelActive:
            tip_box = pygame.Surface((screenWide, 160), pygame.SRCALPHA)
            tip_box.fill((0, 0, 0, 150))
            screen.blit(tip_box, (0, 50))
            for idx, line in enumerate(tutorialLines):
                tip_text = miniFont.render(line, True, whiteColor)
                screen.blit(tip_text, (screenWide // 2 - tip_text.get_width() // 2, 70 + idx * 28))
        drawPlayer()

        levelLabel = "Tutorial" if tutorialLevelActive else f"Level {levelNumber}"
        hudLevel = miniFont.render(levelLabel, True, whiteColor)
        screen.blit(hudLevel, (10, 10))
        levelSeconds = (nowTime - levelStartTick) / 1000
        hudTime = miniFont.render(f"Time {levelSeconds:.1f}s", True, whiteColor)
        screen.blit(hudTime, (10, 34))
        for idx, text in enumerate(puzzleMessages()):
            msgSurf = miniFont.render(text, True, whiteColor)
            screen.blit(msgSurf, (10, 70 + idx * 24))
        if levelLine:
            lineSurf = miniFont.render(levelLine, True, whiteColor)
            screen.blit(lineSurf, (10, screenTall - 70))
        if unlockFlashTime and nowTime - unlockFlashTime < 1800:
            flashSurf = mediumFont.render("EXIT IS OPEN!!!", True, exitOpenColor)
            screen.blit(flashSurf, flashSurf.get_rect(center=(screenWide // 2, 80)))
        if cooldownWords and nowTime - cooldownTime < 1100:
            cdSurf = miniFont.render(cooldownWords, True, (255, 90, 90))
            cdRect = cdSurf.get_rect(center=(screenWide // 2, screenTall - 90))
            screen.blit(cdSurf, cdRect)
            barWidth = 260
            progress = min((nowTime - lastEchoTime) / echoDelay, 1.0)
            barRect = pygame.Rect(screenWide // 2 - barWidth // 2, screenTall - 70, barWidth, 16)
            pygame.draw.rect(screen, (70, 70, 70), barRect)
            pygame.draw.rect(screen, (0, 160, 255), (barRect.x, barRect.y, int(barWidth * progress), 16))
            pygame.draw.rect(screen, whiteColor, barRect, 2)

        if playerBox.colliderect(exitBox) and not exitLocked:
            screen.fill(blackColor)
            winText = bigFont.render("You escaped!", True, exitOpenColor)
            lvlText = mediumFont.render(f"Level {levelNumber} complete!", True, whiteColor)
            ideaText = miniFont.render(random.choice(victoryBlurbs), True, whiteColor)
            screen.blit(winText, winText.get_rect(center=(screenWide // 2, screenTall // 2 - 40)))
            screen.blit(lvlText, lvlText.get_rect(center=(screenWide // 2, screenTall // 2 + 10)))
            screen.blit(ideaText, ideaText.get_rect(center=(screenWide // 2, screenTall // 2 + 50)))
            pygame.display.flip()
            pygame.time.delay(1600)
            levelNumber += 1
            echoDelay = max(600, 2000 - levelNumber * 120)
            startLevel()
            continue

        pygame.display.flip()
        clock.tick(60)

pygame.quit()
sys.exit()
