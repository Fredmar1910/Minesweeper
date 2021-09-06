import pygame, msLogic
import numpy as np
from sys import exit

# TODO Check if map is randomized uniformly
# TODO Display multiple exploded bombs
# TODO Menu
# TODO Highscores file
# TODO Ros background
# TODO Win/lose animation
# TODO Half open animation
# TODO adjustable cellsize (fonts and shadow)

def main():
    ctrl = Control("expert")
    
    while ctrl.mode:
        if ctrl.mode == 'game':
            gameMode(ctrl)
        elif ctrl.mode == 'sandbox':
            sandboxMode(ctrl)
        else:
            print('Mode not recognized')
            exit()
            
    print('Thanks for playing')

class Control:
    def __init__(self, difficulty='expert', mode='game') -> None:
        self.mode = mode  # Default mode
        self.difficulties = {'easy': (9, 9, 10), 'hard': (16, 16, 40), 'expert': (30, 16, 99)}
        if difficulty in self.difficulties:
            self.w, self.h, self.bombs = self.difficulties[difficulty]
        else:  # Custom difficulty
            self.w, self.h = difficulty
            
        self.cellSize = 30  # Pixels? Font works best with size = 40
        self.offSetW, self.offSetH = 0, 0
        self.screen = pygame.display.set_mode((self.cellSize*self.w,
                                               self.cellSize*self.h))
        self.drawImages()

    def drawImages(self):
        cellSize = self.cellSize
        images = {}
        colorScale = ['white', (240,240,240), (211,211,211), (192,192,192), (169,169,169), (100,100,100), (105,105,105)]
        
        # Drawing empty cell
        emptyCell = pygame.Surface((cellSize, cellSize))
        border = pygame.Rect((0, 0), (cellSize, cellSize))
        pygame.draw.rect(emptyCell, colorScale[5], border, width = 1)
        
        # Drawing closed cell
        closedBackground = pygame.Surface((cellSize, cellSize))
        closedBackground.fill(colorScale[4])
        pygame.draw.rect(closedBackground, colorScale[5], border, width = 1)
        sw = 3
        # Shadows
        # Dark horisontal
        pygame.draw.line(closedBackground, colorScale[3], (1, cellSize-2-sw//2),
                        (cellSize-2, cellSize-2-sw//2), width=sw)
        # Dark vertical
        pygame.draw.line(closedBackground, colorScale[3], (cellSize-sw//2-2, 1),
                        (cellSize-sw//2-2, cellSize-2), width=sw)
        # Light vertical
        pygame.draw.line(closedBackground, colorScale[1], (1, 1+(sw-1)//2),
                        (cellSize-2, 1+(sw-1)//2), width=sw)
        # Light horizontal
        pygame.draw.line(closedBackground, colorScale[1], (1+(sw-1)//2, 1),
                        (1+(sw-1)//2, cellSize-2), width=sw)

        
        images['closed'] = closedBackground.copy()
        
        imageNames = {'flag': 'closed', 'half': 'closed', 'bomb': 'empty'}
        
        for imageName, backgroundValue in imageNames.items():
            filepath = "images/" + imageName + ".png"
            icon = pygame.image.load(filepath).convert_alpha()
            icon = pygame.transform.scale(icon, (cellSize, cellSize))
            if backgroundValue == 'closed':
                back = closedBackground.copy()
            elif backgroundValue == 'empty':
                back = emptyCell.copy()
            back.blit(icon, (0,0))
            images[imageName] = back
        
        
        # Drawing bomb explosion
        exploded = images['bomb'].copy()
        lineWidth = 3
        redRect = pygame.Rect((lineWidth, lineWidth), (cellSize-lineWidth*2, cellSize-lineWidth*2))
        pygame.draw.rect(exploded, 'red', redRect, width=lineWidth)
        images['exploded'] = exploded
        
        # Drawing wrong flag
        wrongFlag = images['flag'].copy()
        ofset = 3
        pygame.draw.line(wrongFlag, 'red', (ofset, ofset), (cellSize-ofset, cellSize-ofset))
        pygame.draw.line(wrongFlag, 'red', (ofset, cellSize-ofset), (cellSize-ofset, ofset))
        images['wrongFlag'] = wrongFlag
        
        # Drawing numbers
        # 0:
        images['0'] = emptyCell.copy()
        
        # 1-8:
        pygame.font.init()
        myfont = pygame.font.SysFont('connectioniii', 20, bold=True)
        colours = ['blue', 	(0,128,0), 	'dark red', 'dark blue', 'brown', 'turquoise', 'black', 'gray']
        for i in range(1, 9):
            text = myfont.render(str(i), False, colours[i-1])
            number = emptyCell.copy()
            number.blit(text, (10,6))
            images[str(i)]= number
        
        self.images = images 
        
        background = pygame.Surface((cellSize*self.w,cellSize*self.h))
        background.fill('white')  
        self.background = background     

def sandboxMode(ctrl):
    cellSize = ctrl.cellSize
    sandbox = Sandbox(ctrl.w, ctrl.h)
    
    while True:
        # Eventhandler
        for event in pygame.event.get():
            # Not dependent on isGameOver
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
            # Dependent on active game
            if event.type == pygame.MOUSEBUTTONUP:
                #print(event)
                if event.button == 1:
                    pos = event.pos
                    i, j = pos[0] // cellSize, pos[1] // cellSize
                    sandbox.open(i, j)
                elif event.button == 3:
                    pass
                
            elif event.type == pygame.KEYDOWN:
                if event.key == 32:  # Spacebar functions
                    pass
                    #print(event)
        
        # Displaying background
        ctrl.screen.blit(ctrl.background, (ctrl.offSetW, ctrl.offSetW))
        
        # Displaying cells
        for j in range(sandbox.h):
            for i in range(sandbox.w):  
                ctrl.screen.blit(ctrl.images[sandbox.display[j][i]],
                    (ctrl.offSetW+i*cellSize, ctrl.offSetH+j*cellSize))
        
        pygame.display.update()

def gameMode(ctrl):
    cellSize = ctrl.cellSize
    game = Game(ctrl.w, ctrl.h, ctrl.bombs)

    clock = pygame.time.Clock()

    while True:
        # Eventhandler
        for event in pygame.event.get():
            # Not dependent on isGameOver
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == 114:  # Reset by pressing 'r'
                    game.reset()
                
            # Dependent on active game
            if not game.isGameOver:
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = event.pos
                    i, j = pos[0] // cellSize, pos[1] // cellSize
                    # Left click to open
                    if event.button == 1 and game.display[j][i] in ['closed', 'half']:
                        if not game.correctBoard:
                            game.start(i, j)
                        game.open(i,j)
                    #print(event)
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == 32:  # Spacebar functions
                        pos = pygame.mouse.get_pos()
                        i, j = pos[0] // cellSize, pos[1] // cellSize
                        displayed = game.display[j][i]
                        if displayed in ['closed', 'half']:
                            game.display[j][i] = 'flag'
                            game.bombs_left -= 1
                            print("Bombs left:", game.bombs_left)
                        elif displayed == 'flag':
                            game.display[j][i] = 'closed'
                            game.bombs_left += 1
                            print("Bombs left:", game.bombs_left)
                        elif displayed != 'bomb':
                            neighbours = msLogic.getNeighbours(i, j, game.w, game.h)
                            neighbouringFlags = 0
                            for neighPos in neighbours:
                                if game.display[neighPos[1]][neighPos[0]] == 'flag':
                                    neighbouringFlags += 1
                            if neighbouringFlags == int(displayed):
                                game.openNeighbours(i, j)
                            
                    #print(event)
        
        # Displaying background
        ctrl.screen.blit(ctrl.background, (ctrl.offSetW, ctrl.offSetW))
        
        # Displaying cells
        for j in range(game.h):
            for i in range(game.w):  
                ctrl.screen.blit(ctrl.images[game.display[j][i]],
                    (ctrl.offSetW+i*cellSize, ctrl.offSetH+j*cellSize))
        
        # Clock
        clock.tick()
        if game.isStarted:
            game.time += clock.get_time()
        
        pygame.display.update()

class Board:
    def __init__(self, w, h) -> None:
        self.w = w
        self.h = h
        
    def initCorrectBoard(self, map):
            correctBoard = []
            for j in range(self.h):
                row = []
                for i in range(self.w):
                    cellValue = map[j, i]
                    if cellValue > 9:
                        cellValue = 'bomb'
                    else:
                        cellValue = str(int(cellValue))
                    row.append(cellValue)
                correctBoard.append(row)
            return correctBoard
        
class Sandbox(Board):
    def __init__(self, w, h) -> None:
        super().__init__(w, h)
        self.display = [['0' for i in range(w)]for j in range(h)]
        self.logicMap = np.array([[0 for i in range(w)] for j in range(h)])
        
    def open(self, i, j):
        if self.display[j][i] == 'bomb':
            self.logicMap[j, i] -= 10
            msLogic.bombIncrement(self.logicMap, i, j, amount=-1)
            self.display = self.initCorrectBoard(self.logicMap)
        else:
            self.logicMap[j][i] += 10
            msLogic.bombIncrement(self.logicMap, i, j)
            self.display = self.initCorrectBoard(self.logicMap)

class Game(Board):
    def __init__(self, w, h, bombs):
        super().__init__(w, h) 
        self.bombs = bombs
        self.tiles = w*h
        self.isGameOver = False
        self.isStarted = False
        
        self.correctBoard = None
        self.display = [['closed' for i in range(w)]for j in range(h)]
        
        self.toOpen = self.tiles - bombs
        self.bombs_left = bombs
        
        self.time = 0
    
    def start(self, i, j):
        map = msLogic.makeMinesweeperMap(self.w, self.h, self.bombs, (i, j))
        self.correctBoard = self.initCorrectBoard(map)
        self.isStarted = True
        
    def reset(self):
        self.isGameOver = False
        
        self.correctBoard = None
        self.display = [['closed' for i in range(self.w)]for j in range(self.h)]
        
        self.time = 0
        self.toOpen = self.tiles - self.bombs
        self.bombs_left = self.bombs
    
    def gameOver(self):
        self.isGameOver = True
        self.isStarted = False
        
        for j in range(self.h):
            for i in range(self.w):
                if self.correctBoard[j][i] == 'bomb':
                    if self.display[j][i] == 'closed':
                        self.display[j][i] = 'bomb'
                else:
                    if self.display[j][i] == 'flag':
                         self.display[j][i] = 'wrongFlag'
                    
        print("You dieded")
        
    def youWin(self):
        self.isGameOver = True
        self.isStarted = False
        self.display = list(map(lambda row: list(map(lambda cell: 'flag' if cell == 'bomb' else cell, row)), self.correctBoard))
        print("-"*10, "You won", "-"*10)
        print("Your time was:", round(self.time / 1000, 3)) 
        
    def open(self, i, j):
        lookup = self.correctBoard[j][i]
        if lookup == "bomb":
            self.gameOver()
            self.display[j][i] = 'exploded'
        else: 
            self.display[j][i] = lookup
            self.decreaseToOpen()
            if lookup == '0':
                self.openNeighbours(i, j)
                
    def openNeighbours(self, i, j):
        for pos in msLogic.getNeighbours(i, j, self.w, self.h):
            if self.display[pos[1]][pos[0]] == 'closed':
                self.open(pos[0], pos[1])
    
    def decreaseToOpen(self):
        self.toOpen -= 1
        if self.toOpen == 0:
            self.youWin()
        else:
            print("Open", self.toOpen, "more")              

if __name__ == '__main__':
    main()