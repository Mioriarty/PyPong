# ****** LINKS ******
# COPYRIGHT by Mortz Seppelt
# Images created by myself with GIMP: https://www.gimp.org
# Sounds created with Bfxr: http://www.bfxr.net
# Music: "Korobeiniki" by Unknown (russian folk-dance)
# Font ModerDOS created by Jayvee Enaguas: https://www.dafont.com/moder-dos-437.font

# ****** IMPORTS ******
import pygame
import random

# ****** PUBLIC VARS ******

menu = None
game = None
font = None

# ****** CLASSES ******

# basic classes

class GameObject:
    
    allObjects = []

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.active = True
        GameObject.allObjects.append(self)    
    
    def update(self):
        pass

    def updateAll():
        for o in GameObject.allObjects:
            if(o.active):
                o.update()

    def setActiveAll(isActive):
        for o in GameObject.allObjects:
            o.active = isActive

    def clearReferences():
        GameObject.allObjects = []



class Actor(GameObject):
    def __init__(self, imageLocation):
        GameObject.__init__(self)
        self.image = pygame.image.load(imageLocation)
        self.width = self.image.get_rect().size[0]
        self.height = self.image.get_rect().size[1]


    def setImageSize(self, width, height):
        self.image = pygame.transform.scale(self.image, (width, height))
        self.width = width
        self.height = height

class Font:
    def __init__(self, fontName, size):
        self.font = pygame.font.Font(fontName, size)
        self.fontName = fontName
        self.size = size

    def setSize(size):
        self.__init__(self.fontName, size)

class TextField(GameObject):
    def __init__(self, text, font, color):
        GameObject.__init__(self)
        self.surface = font.font.render(text, False, color)
        self.rect = self.surface.get_rect()
        self.text = text
        self.font = font
        self.color = color

    def reset(self, text, font, color):
        self.surface = font.font.render(text, False, color)
        self.rect = self.surface.get_rect()
        self.text = text
        self.font = font
        self.color = color
        self.update()

    def setText(self, text):
        self.reset(text, self.font, self.color)

    def update(self):
        self.rect.center = (self.x, self.y)


class Display:
    def __init__(self, width, height, title, fps = 60):
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.quit = False
        self.fps = fps
        self.clearColor = (0, 0, 0)
        self.width = width
        self.height = height
        self.timeScale = 1
        self.keysDown = {}
        self.keysJustDown = {}
        pygame.display.set_caption(title)

    def update(self):
        # update screen
        pygame.display.update()
        self.clock.tick(self.fps)
        self.screen.fill(self.clearColor)

        # handle events
        self.keysJustDown = {}
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            if event.type == pygame.KEYDOWN:
                self.keysDown[event.key] = True
                self.keysJustDown[event.key] = True
            if event.type == pygame.KEYUP:
                self.keysDown[event.key] = False

    
    def close(self):
        pygame.quit()

    
    def isCloseRequested(self):
        return self.quit

    def drawActor(self, actor):
        self.screen.blit(actor.image, (actor.x, actor.y))
    
    def drawTextField(self, textField):
        self.screen.blit(textField.surface, textField.rect)

    def drawAll(self):
        for o in GameObject.allObjects:
            if(o.active):
                if(isinstance(o, Actor)):
                    self.drawActor(o)
                elif(isinstance(o, TextField)):
                    self.drawTextField(o)
            

    def getDTime(self):
        return 1/self.fps * self.timeScale

    def isKeyDown(self, keyCode):
        if keyCode in self.keysDown:
            return self.keysDown[keyCode]
        else:
            return False

    def keyJustPressed(self, keyCode):
        return keyCode in self.keysJustDown


class Board(Actor):


    def __init__(self, isLeft):
        Actor.__init__(self, "pixel.png")
        self.setImageSize(18, 100)
        self.y = display.height / 2
        self.isAi = False
        self.normalMoveSpeed = 500
        self.aiMoveSpeed = 200
        self.upKey = pygame.K_UP
        self.downKey = pygame.K_DOWN
        if(isLeft):
            self.x = display.width / 11
        else:
            self.x = display.width - display.width / 11

    def update(self):
        if self.isAi:
            # simple board ai
            reactionLineTop = self.y + self.height * 0.33
            reactionLineBottom = self.y + self.height * 0.67
            if game.ball.y < reactionLineTop:
                self.y -= self.aiMoveSpeed * display.getDTime()
            elif game.ball.y > reactionLineBottom:
                self.y += self.aiMoveSpeed * display.getDTime()
            else:
                self.y += max(min(game.ball.veloY, self.aiMoveSpeed), -self.aiMoveSpeed) * display.getDTime()
            
        else:
            # simple move script
            if display.isKeyDown(self.upKey):
                self.y -= self.normalMoveSpeed * display.getDTime()
            if display.isKeyDown(self.downKey):
                self.y += self.normalMoveSpeed * display.getDTime()
        
        # clamp the y value to not overshoot the screen borders
        self.y = max(min(self.y, display.height - self.height), 0)
                



class Ball(Actor):
    def __init__(self):
        Actor.__init__(self, "pixel.png")
        self.setImageSize(15, 15)
        self.moves = False
        self.maxYSpeed = 85
        self.veloY = 0
        self.veloX = 0
        self.collisionCounter = 0
        self.maxXSpeed = 1000
        self.xSpeedIncrease = 33
        self.ySpeedIncrease = 0.4
        self.startSpeedX = 400

    def update(self):
        if self.moves:

            lastX = self.x
            
            #simple moving
            self.x += self.veloX * display.getDTime()
            self.y += self.veloY * display.getDTime()

            #screen border collisions
            if self.y <= 0.0:
                self.veloY = abs(self.veloY)
                game.collisionSound.play()
            
            if self.y >= display.height - self.height:
                self.veloY = - abs(self.veloY)
                game.collisionSound.play()

            if self.x <= 0.0:
                # left screen edge
                game.scoreBoard.pointsR += 1
                game.scoreBoard.updateScoreBoard()
                if not game.scoreBoard.testForEnd():
                    game.pointSound.play()
                    self.spawn()

            if self.x >= display.width - self.width:
                # right screen edge
                game.scoreBoard.pointsL += 1
                game.scoreBoard.updateScoreBoard()
                if not game.scoreBoard.testForEnd():
                    game.pointSound.play()
                    self.spawn()

            # board collisions
            leftCollisionLine = game.boardL.x + game.boardL.width
            rightCollisionLine = game.boardR.x - self.width

            if self.x <= leftCollisionLine and lastX > leftCollisionLine:
                boardMax = game.boardL.y + game.boardL.height
                if self.y >= game.boardL.y - self.height * 1.5 and self.y <= boardMax:
                    # left collision
                    self.veloX = min(abs(self.veloX) + self.xSpeedIncrease, self.maxXSpeed)
                    self.collisionCounter += 1
                    game.collisionSound.play()
                    self.calcNewYSpeed(game.boardL)

            elif self.x >= rightCollisionLine and lastX < rightCollisionLine:
                boardMax = game.boardR.y + game.boardR.height
                if self.y >= game.boardR.y - self.height * 1.5 and self.y <= boardMax:
                    # right collision
                    self.veloX = -min(abs(self.veloX) + self.xSpeedIncrease, self.maxXSpeed)
                    self.collisionCounter += 1
                    game.collisionSound.play()
                    self.calcNewYSpeed(game.boardR)

    def calcNewYSpeed(self, board):
        y = (self.y + self.height / 2) - board.y # gets delta y position
        y = y / board.height # puts delta y position between 0 and 1
        y = y * 2 - 1 # puts that between -1 and 1
        y = y * self.maxYSpeed # converts this into a proper speed
        y = y * (1 + self.collisionCounter * self.ySpeedIncrease) # adds increasing difficulty
        self.veloY = y

    
    def spawn(self): # respawns the ball and resets all properties
        self.x = display.width / 2 - self.width / 2
        self.collisionCounter = 0
        self.y = random.randint(display.height / 4, display.height / 4 * 3 - self.height)
        if random.random() > 0.5:
            self.veloX = self.startSpeedX
        else:
            self.veloX = -self.startSpeedX

        self.veloY = random.uniform(-self.maxYSpeed, self.maxYSpeed)
        self.moves = True


class MiddleLine(Actor):
    def __init__(self):
        Actor.__init__(self, "middle.png")
        self.setImageSize(int(display.width / 100), display.height)
        self.x = display.width / 2 - self.width / 2


class ScoreBoard(GameObject):
    def __init__(self):
        self.pointsL = 0
        self.pointsR = 0
        self.maxPoints = 10

    def updateScoreBoard(self):
        game.scoreL.setText(str(self.pointsL))
        game.scoreR.setText(str(self.pointsR))
        if(self.testForEnd()):
            # figuring out the name of the player who has won
            if(game.multiplayer):
                if(self.pointsL >= self.maxPoints):
                    game.winSound.play()
                    game.lose("Player 1")
                else:
                    game.loseSound.play()
                    game.lose("Player 2")
            else:
                if(self.pointsL >= self.maxPoints):
                    game.winSound.play()
                    game.lose("You")
                else:
                    game.loseSound.play()
                    game.lose("The Computer")

            

    def testForEnd(self):
        return self.pointsL >= self.maxPoints or self.pointsR >= self.maxPoints

class EndScreenText(TextField):
    def __init__(self, playerName):
        TextField.__init__(self, playerName + " won!", font, (255, 255, 255))
        self.x = display.width / 2
        self.y = display.height / 2
        TextField.update(self)
        
    def update(self):
        global shouldSwitch     
        if(display.keyJustPressed(pygame.K_RETURN)):
            shouldSwitch = True

        TextField.update(self)

class MainMenu(GameObject):
    def __init__(self, maxPoints):
        GameObject.__init__(self)
        self.isMainMenu = True
        self.buttonDistance = 100
        self.difficulty = 0
        self.difficultyMap = {-2: "Very Easy", -1: "Easy", 0: "Average", 1: "Hard", 2: "Demon", 3: "Impossible"}
        self.curserPosition = -1
        self.maxPoints = maxPoints
        self.buttonWidth = 230
        self.buttonOne = TextField("One Player", font, (255, 255, 255))
        self.buttonOne.x = display.width / 2
        self.buttonOne.y = display.height / 2 - self.buttonDistance
        self.buttonMulti = TextField("Two Players", font, (255, 255, 255))
        self.buttonMulti.x = display.width / 2
        self.buttonMulti.y = display.height / 2
        self.buttonPoints = TextField("Max. Points: " + str(self.maxPoints), font, (255, 255, 255))
        self.buttonPoints.x = display.width / 2
        self.buttonPoints.y = display.height / 2 + self.buttonDistance
        self.buttonDifficulty = TextField("", font, (255, 255, 255))
        self.buttonDifficulty.x = display.width / 2
        self.buttonDifficulty.y = display.height / 2
        self.buttonDifficulty.active = False


        self.arrowL = Actor("arrowL.png")
        self.arrowL.setImageSize(40, 60)
        self.arrowR = Actor("arrowR.png")
        self.arrowR.setImageSize(40, 60)
        self.updateArrowPosition(False)

        self.selectSound = Sound("menu_select.wav")

        self.multiplayerRequested = False

    def updateArrowPosition(self, reversed):
        y = display.height / 2 + self.curserPosition * self.buttonDistance - self.arrowL.height / 2
        self.arrowL.y = y
        self.arrowR.y = y

        if reversed:
            self.arrowR.x = display.width / 2 - self.buttonWidth - self.arrowR.width
            self.arrowL.x = display.width / 2 + self.buttonWidth
        else:
            self.arrowL.x = display.width / 2 - self.buttonWidth - self.arrowL.width
            self.arrowR.x = display.width / 2 + self.buttonWidth

    def update(self):
        global shouldSwitch
        if self.isMainMenu:
            if(display.keyJustPressed(pygame.K_UP)):
                self.curserPosition -= 1
                self.selectSound.play()
            if(display.keyJustPressed(pygame.K_DOWN)):
                self.curserPosition += 1
                self.selectSound.play()

            self.curserPosition = max(min(self.curserPosition, 1), -1)

            if self.curserPosition == 1:
                changed = False
                if(display.keyJustPressed(pygame.K_RIGHT)):
                    self.maxPoints += 1
                    changed = True
                if(display.keyJustPressed(pygame.K_LEFT)):
                    self.maxPoints -= 1
                    changed = True
                if(changed):
                    self.maxPoints = max(min(self.maxPoints, 25), 1)
                    self.selectSound.play()
                    self.buttonPoints.setText("Max. Points: " + str(self.maxPoints))
            else:
                if(display.keyJustPressed(pygame.K_RETURN)):
                    
                    self.multiplayerRequested = self.curserPosition == 0
                    if self.multiplayerRequested:
                        shouldSwitch = True
                    else:
                        # start second menu
                        GameObject.setActiveAll(False)
                        self.buttonDifficulty.active = True
                        self.buttonDifficulty.setText(self.difficultyMap[self.difficulty])
                        self.curserPosition = 0
                        self.arrowL.active = True
                        self.arrowR.active = True
                        self.isMainMenu = False
                        self.active = True
                        
                        
            
            self.updateArrowPosition(self.curserPosition == 1 or not self.isMainMenu)
        else:
            changed = False
            if display.keyJustPressed(pygame.K_LEFT):
                self.difficulty -= 1
                changed = True
            if display.keyJustPressed(pygame.K_RIGHT):
                self.difficulty += 1
                changed = True

            self.difficulty = max(min(self.difficulty, 3), -2)

            if changed:
                self.buttonDifficulty.setText(self.difficultyMap[self.difficulty])
                menu.selectSound.play()

            if display.keyJustPressed(pygame.K_RETURN):
                shouldSwitch = True
        


class Game:
    def __init__(self, isMultiplayer):
        self.multiplayer = isMultiplayer
        self.difficultyToSpeed = {-2: 100, -1: 175, 0: 270, 1: 360, 2: 450, 3: 850}

        self.scoreL = TextField("0", font, (255, 255, 255))
        self.scoreR = TextField("0", font, (255, 255, 255))
        self.scoreL.y = display.height / 9
        self.scoreR.y = display.height / 9
        self.scoreL.x = display.width / 4
        self.scoreR.x = display.width / 4 * 3

        self.middle = MiddleLine()
        self.scoreBoard = ScoreBoard()
        self.scoreBoard.maxPoints = 2

        self.boardL = Board(True)
        self.boardR = Board(False)

        self.collisionSound = Sound("hit.wav")
        self.pointSound = Sound("losePoint.wav")
        self.loseSound = Sound("gameEnd_neg.wav")
        self.winSound = Sound("gameEnd_pos.wav")

        if self.multiplayer:
            self.boardL.upKey = pygame.K_w
            self.boardL.downKey = pygame.K_s
        else:
            self.boardR.isAi = True
            self.boardR.aiMoveSpeed = self.difficultyToSpeed[difficulty]

        self.ball = Ball()
        self.ball.spawn()

    def lose(self, playerName):
        GameObject.setActiveAll(False)
        self.scoreL.active = True
        self.scoreR.active = True
        endScreenText = EndScreenText(playerName)

class Sound:
    def __init__(self, file):
        self.data = pygame.mixer.Sound(file)

    def play(self):
        pygame.mixer.Sound.play(self.data)

    def setBgMusic(file):
        pygame.mixer.music.load(file)

    def playBgMusic():
        pygame.mixer.music.play(-1)
    
    def stopBgMusic():
        pygame.mixer.music.stop()

def switchGameAndMenu():
    global menu, game, shouldSwitch, maxPoints, difficulty
    if menu == None: # game is running
        game = None # stop game
        GameObject.clearReferences() # clears all references
        menu = MainMenu(maxPoints) # start menu
        menu.difficulty = difficulty
    else: # menu is running
        mulplayer = menu.multiplayerRequested
        maxPoints = menu.maxPoints
        difficulty = menu.difficulty
        menu = None # stop menu
        GameObject.clearReferences() # clears all references
        game = Game(mulplayer) # start game
        game.scoreBoard.maxPoints = maxPoints

    shouldSwitch = False


# ****** MAIN PROGRAM ******

pygame.init()
pygame.font.init()
pygame.mouse.set_visible(False)
display = Display(1000, 600, "PyPong", 60)
display.clearColor = (0, 0, 0)

font = Font("ModernDOS.ttf", 50)

shouldSwitch = False
maxPoints = 10
difficulty = 0

Sound.setBgMusic("tetris_theme.wav")
Sound.playBgMusic()

menu = MainMenu(maxPoints)


while not display.isCloseRequested():
    display.update()
    GameObject.updateAll()
    display.drawAll()
    if(display.isKeyDown(pygame.K_SPACE)):
        display.timeScale = 3
    else:
        display.timeScale = 1

    if(display.keyJustPressed(pygame.K_r) and game != None):
        shouldSwitch = True

    if(shouldSwitch):
        switchGameAndMenu()


display.close()
quit()
