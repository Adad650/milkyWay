import pygame
import random
import math
import time
import sys
import io
import wave
import textwrap
from array import array

pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    print("Warning: audio disabled; continuing without sounds.", file=sys.stderr)
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
resonatorColor = (90, 255, 255)
storyColor = (255, 210, 120)
dashColor = (120, 255, 180)
shieldColor = (255, 250, 170)
hazardColor = (255, 90, 120)
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


def synth_tone(freq, duration_ms, volume=0.4):
    """Generate a sine tone Sound without needing external files."""
    if not pygame.mixer.get_init():
        return None
    sample_rate = 22050
    total_samples = int(sample_rate * duration_ms / 1000)
    amplitude = int(32767 * max(0.0, min(volume, 1.0)))
    data = array("h")
    for i in range(total_samples):
        value = int(amplitude * math.sin(2 * math.pi * freq * (i / sample_rate)))
        data.append(value)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(data.tobytes())
    buffer.seek(0)
    try:
        return pygame.mixer.Sound(file=buffer)
    except pygame.error:
        return None


def play_sound(effect):
    if effect:
        effect.play()


echoSound = synth_tone(660, 140, 0.35)
pickupSound = synth_tone(900, 110, 0.4)
exitSound = synth_tone(520, 200, 0.45)
shieldSound = synth_tone(220, 200, 0.45)
dashSound = synth_tone(1040, 160, 0.35)

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
baseEchoDelay = echoDelay
comboWindow = 2500
lastEchoTime = 0
cooldownWords = ""
cooldownTime = 0
echoBoostEndTime = 0
comboBoostEndTime = 0
echoComboCount = 0
lastComboTime = 0

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

storyFragments = [
    "Dispatch Log 17A: Prototype Echo Bot 6 (you) went missing in this wing.",
    "Memo: The maze keeps shifting so intruders never reach the broadcast tower.",
    "Journal: I left memory shards around—collect them to remember why we're here.",
    "Studio Note: The boss wants camera footage, but I'd rather free the tiny bots.",
    "Final Reminder: Reach the broadcast core and tell the city what happened."
]
storyIndex = 0
storyPopup = ""
storyPopupTime = 0
storyPopupDuration = 6000

collectibles = []
resonatorsFound = 0
resonatorsThisLevel = 0
speedBoostEndTime = 0
speedBoostMultiplier = 1.35
shieldCharges = 0
maxShieldCharges = 2
statusMessage = ""
statusMessageTime = 0
statusMessageDuration = 2800
staticFields = []
hazardGraceTime = 0

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


def makeCollectibles(level, grid):
    spots = getOpenSpots(grid)
    random.shuffle(spots)

    def rect_from_spot():
        x, y = takeSpot(spots)
        return pygame.Rect(x * cellSize + 12, y * cellSize + 12, cellSize - 24, cellSize - 24)

    items = []
    if storyIndex < len(storyFragments):
        items.append({
            "type": "story",
            "rect": rect_from_spot(),
            "text": storyFragments[storyIndex],
            "pulse": random.randint(0, 400)
        })
    resonator_count = min(2 + level // 2, 5)
    for _ in range(resonator_count):
        if not spots:
            break
        items.append({
            "type": "resonator",
            "rect": rect_from_spot(),
            "pulse": random.randint(0, 400)
        })
    dash_count = 1 + level // 3
    for _ in range(dash_count):
        if not spots:
            break
        items.append({
            "type": "dash",
            "rect": rect_from_spot(),
            "pulse": random.randint(0, 500)
        })
    if level >= 2:
        shield_count = 1 if level < 5 else 2
        for _ in range(shield_count):
            if not spots:
                break
            items.append({
                "type": "shield",
                "rect": rect_from_spot(),
                "pulse": random.randint(0, 600)
            })
    return items


def makeStaticFields(level, grid):
    hazardCount = min(3 + level, 8)
    tiles = getOpenSpots(grid)
    random.shuffle(tiles)
    hazards = []
    for _ in range(hazardCount):
        if not tiles:
            break
        x, y = takeSpot(tiles)
        hazards.append({
            "rect": pygame.Rect(x * cellSize + 8, y * cellSize + 8, cellSize - 16, cellSize - 16),
            "pulse": random.randint(0, 300)
        })
    return hazards


def handleEchoCombo(nowTicks):
    global echoComboCount, lastComboTime, comboBoostEndTime, statusMessage, statusMessageTime
    global levelLine, lineTimer
    if nowTicks - lastComboTime <= comboWindow:
        echoComboCount += 1
    else:
        echoComboCount = 1
    lastComboTime = nowTicks
    if echoComboCount >= 3:
        comboBoostEndTime = nowTicks + 5000
        statusMessage = f"Echo combo x{echoComboCount}! cooldown slashed."
        statusMessageTime = nowTicks
        levelLine = "Chain echoes to keep the combo alive!"
        lineTimer = nowTicks


def refreshEchoDelay(nowTicks):
    global echoDelay, echoBoostEndTime, comboBoostEndTime, echoComboCount
    delay = baseEchoDelay
    if echoComboCount and nowTicks - lastComboTime > comboWindow:
        echoComboCount = 0
    if echoBoostEndTime and nowTicks >= echoBoostEndTime:
        echoBoostEndTime = 0
    if comboBoostEndTime and nowTicks >= comboBoostEndTime:
        comboBoostEndTime = 0
    if echoBoostEndTime:
        delay = min(delay, int(baseEchoDelay * 0.45))
    if comboBoostEndTime:
        delay = min(delay, int(baseEchoDelay * 0.35))
    echoDelay = max(250, delay)


def checkStaticFields(nowTicks):
    global shieldCharges, statusMessage, statusMessageTime, playerBox, hazardGraceTime
    if not staticFields or nowTicks < hazardGraceTime:
        return
    for field in staticFields:
        if playerBox.colliderect(field["rect"]):
            hazardGraceTime = nowTicks + 1200
            if shieldCharges:
                shieldCharges -= 1
                statusMessage = "Shield absorbed static shock!"
                statusMessageTime = nowTicks
            else:
                playerBox.center = (cellSize // 2, cellSize // 2)
                statusMessage = "Static field zapped you to start!"
                statusMessageTime = nowTicks
            break


def drawStaticFields():
    if not staticFields:
        return
    now = pygame.time.get_ticks()
    for field in staticFields:
        rect = field["rect"]
        pulse = 2 + int(2 * math.sin((now + field["pulse"]) / 180))
        blow = pygame.Rect(rect.x - pulse, rect.y - pulse, rect.width + pulse * 2, rect.height + pulse * 2)
        pygame.draw.rect(screen, (hazardColor[0], hazardColor[1], hazardColor[2],), blow, 2)
        pygame.draw.rect(screen, hazardColor, rect)


def startLevel():
    global mazeMap, mazeWalls, exitBox, playerBox, puzzlesNow, exitLocked, unlockFlashTime
    global levelStartTick, levelLine, lineTimer, gameStarted, screen, cooldownWords, cooldownTime, lastEchoTime
    global currentWallColor, currentFloorColor, tutorialLevelActive, tutorialLines
    global collectibles, resonatorsFound, resonatorsThisLevel, baseEchoDelay, echoBoostEndTime, storyPopup, storyPopupTime
    global speedBoostEndTime, shieldCharges, staticFields
    global echoComboCount, comboBoostEndTime, lastComboTime, hazardGraceTime
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
    collectibles.clear()
    collectibles.extend(makeCollectibles(levelNumber, mazeMap))
    resonatorsFound = 0
    resonatorsThisLevel = sum(1 for item in collectibles if item["type"] == "resonator")
    baseEchoDelay = echoDelay
    echoBoostEndTime = 0
    comboBoostEndTime = 0
    echoComboCount = 0
    lastComboTime = 0
    storyPopup = ""
    storyPopupTime = 0
    speedBoostEndTime = 0
    shieldCharges = 0
    staticFields = makeStaticFields(levelNumber, mazeMap) if not tutorialLevelActive else []
    hazardGraceTime = 0
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


def updateCollectibles(nowTicks):
    global collectibles, resonatorsFound, storyIndex, storyPopup, storyPopupTime
    global echoDelay, echoBoostEndTime, cooldownWords, cooldownTime
    global speedBoostEndTime, shieldCharges, levelLine, lineTimer
    global statusMessage, statusMessageTime
    changed = False
    for item in collectibles[:]:
        if playerBox.colliderect(item["rect"]):
            collectibles.remove(item)
            if item["type"] == "resonator":
                play_sound(pickupSound)
                resonatorsFound += 1
                echoBoostEndTime = nowTicks + 6000
                echoDelay = max(350, int(baseEchoDelay * 0.45))
                cooldownWords = "Echo boost active!"
                cooldownTime = nowTicks
            elif item["type"] == "story":
                play_sound(pickupSound)
                storyPopup = item["text"]
                storyPopupTime = nowTicks
                storyIndex += 1
            elif item["type"] == "dash":
                speedBoostEndTime = nowTicks + 6000
                statusMessage = "Thrusters engaged! you're faster."
                statusMessageTime = nowTicks
                levelLine = "Thrusters help you sprint faster!"
                lineTimer = nowTicks
                play_sound(dashSound)
            elif item["type"] == "shield":
                shieldCharges = min(maxShieldCharges, shieldCharges + 1)
                statusMessage = f"Shield charge stored ({shieldCharges}/{maxShieldCharges})"
                statusMessageTime = nowTicks
                levelLine = "Shields block one wall smack."
                lineTimer = nowTicks
                play_sound(shieldSound)
            changed = True
    if echoBoostEndTime and nowTicks > echoBoostEndTime:
        echoDelay = baseEchoDelay
        echoBoostEndTime = 0
    if speedBoostEndTime and nowTicks > speedBoostEndTime:
        speedBoostEndTime = 0
    return changed


def drawCollectibles():
    now = pygame.time.get_ticks()
    for item in collectibles:
        cx, cy = item["rect"].center
        pulse = 3 + int(3 * math.sin((now + item["pulse"]) / 200))
        if item["type"] == "resonator":
            pygame.draw.circle(screen, resonatorColor, (cx, cy), 8 + pulse)
            pygame.draw.circle(screen, whiteColor, (cx, cy), 4 + pulse // 2, 2)
        elif item["type"] == "story":
            points = [
                (cx, item["rect"].top - pulse),
                (item["rect"].right + pulse, cy),
                (cx, item["rect"].bottom + pulse),
                (item["rect"].left - pulse, cy)
            ]
            pygame.draw.polygon(screen, storyColor, points)
            pygame.draw.polygon(screen, blackColor, points, 2)
        elif item["type"] == "dash":
            pygame.draw.circle(screen, dashColor, (cx, cy), 10 + pulse, 2)
            pygame.draw.circle(screen, dashColor, (cx, cy), 4 + pulse // 2)
            pygame.draw.line(screen, whiteColor, (cx - 6, cy), (cx + 6, cy), 3)
        elif item["type"] == "shield":
            hex_pts = []
            for i in range(6):
                angle = math.radians(60 * i)
                hex_pts.append((cx + (10 + pulse) * math.cos(angle), cy + (10 + pulse) * math.sin(angle)))
            pygame.draw.polygon(screen, shieldColor, hex_pts)
            pygame.draw.polygon(screen, blackColor, hex_pts, 2)


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
    if shieldCharges:
        pygame.draw.circle(screen, shieldColor, playerBox.center, 28, 2)
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
                    play_sound(echoSound)
                    handleEchoCombo(now)
                    refreshEchoDelay(now)
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
        if speedBoostEndTime and pygame.time.get_ticks() < speedBoostEndTime:
            speed *= speedBoostMultiplier
        playerBox = pushPlayer(playerBox, int(moveX * speed), int(moveY * speed))
        playerBox.clamp_ip(screen.get_rect())

        wasLocked = exitLocked
        allDone = updatePuzzles()
        exitLocked = not allDone
        if wasLocked and not exitLocked:
            unlockFlashTime = pygame.time.get_ticks()
            levelLine = "EXIT IS OPEN!!!"
            lineTimer = unlockFlashTime
            play_sound(exitSound)

        nowTime = pygame.time.get_ticks()
        updateCollectibles(nowTime)
        checkStaticFields(nowTime)
        refreshEchoDelay(nowTime)
        if not tutorialLevelActive and nowTime - lineTimer > 7000:
            levelLine = random.choice(levelNotes)
            lineTimer = nowTime

        screen.fill(spaceColor)
        drawMaze()
        drawCollectibles()
        drawStaticFields()
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
        if resonatorsThisLevel:
            shardText = miniFont.render(f"Echo shards {resonatorsFound}/{resonatorsThisLevel}", True, resonatorColor)
            screen.blit(shardText, (screenWide - shardText.get_width() - 10, 10))
        if echoBoostEndTime:
            remain = max(0, (echoBoostEndTime - nowTime) / 1000)
            boostSurf = miniFont.render(f"Boost {remain:.1f}s", True, resonatorColor)
            screen.blit(boostSurf, (screenWide - boostSurf.get_width() - 10, 34))
        if shieldCharges:
            shieldSurf = miniFont.render(f"Shields {shieldCharges}/{maxShieldCharges}", True, shieldColor)
            screen.blit(shieldSurf, (screenWide - shieldSurf.get_width() - 10, 58))
        if speedBoostEndTime and speedBoostEndTime > nowTime:
            rushRemain = max(0, (speedBoostEndTime - nowTime) / 1000)
            rushSurf = miniFont.render(f"Thrusters {rushRemain:.1f}s", True, dashColor)
            screen.blit(rushSurf, (screenWide - rushSurf.get_width() - 10, 82))
        comboActive = nowTime - lastComboTime <= comboWindow
        if echoComboCount and comboActive:
            comboSurf = miniFont.render(f"Echo combo x{echoComboCount}", True, (255, 255, 140))
            screen.blit(comboSurf, (10, 50))
        status_lines = puzzleMessages()
        if speedBoostEndTime and speedBoostEndTime > nowTime:
            status_lines.append("Thrusters make you sprint faster.")
        if shieldCharges:
            status_lines.append("Shields block the next collision.")
        if staticFields:
            status_lines.append(f"Static fields active: {len(staticFields)}")
        for idx, text in enumerate(status_lines):
            msgSurf = miniFont.render(text, True, whiteColor)
            screen.blit(msgSurf, (10, 70 + idx * 24))
        if levelLine:
            lineSurf = miniFont.render(levelLine, True, whiteColor)
            screen.blit(lineSurf, (10, screenTall - 70))
        logPanel = pygame.Surface((320, 120), pygame.SRCALPHA)
        logPanel.fill((0, 0, 0, 140))
        screen.blit(logPanel, (screenWide - 340, screenTall - 180))
        logLines = [
            f"Story logs {min(storyIndex, len(storyFragments))}/{len(storyFragments)}",
            f"Exit: {'open' if not exitLocked else 'locked'}",
            f"Shields: {shieldCharges}/{maxShieldCharges}",
            f"Thrusters: {'online' if speedBoostEndTime and speedBoostEndTime > nowTime else 'offline'}"
        ]
        for i, text in enumerate(logLines):
            logSurf = miniFont.render(text, True, whiteColor)
            screen.blit(logSurf, (screenWide - 330, screenTall - 165 + i * 24))
        if storyPopup and nowTime - storyPopupTime < storyPopupDuration:
            storySurf = pygame.Surface((screenWide, 90), pygame.SRCALPHA)
            storySurf.fill((10, 10, 20, 200))
            screen.blit(storySurf, (0, screenTall - 200))
            wrapped = textwrap.wrap(storyPopup, 48)
            for idx, text in enumerate(wrapped):
                loreSurf = miniFont.render(text, True, storyColor)
                screen.blit(loreSurf, loreSurf.get_rect(center=(screenWide // 2, screenTall - 170 + idx * 26)))
        if statusMessage and nowTime - statusMessageTime < statusMessageDuration:
            alertSurf = miniFont.render(statusMessage, True, dashColor)
            alertRect = alertSurf.get_rect(center=(screenWide // 2, screenTall - 120))
            screen.blit(alertSurf, alertRect)
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
            play_sound(exitSound)
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
