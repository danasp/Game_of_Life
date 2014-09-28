import sys

import pygame
from pygame.locals import *

pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (139,126,102)

FPS = 2
FPSCLOCK = pygame.time.Clock()

SCREENHEIGHT = 800
SCREENWIDTH = 800
FREESPACE_Y_PERCENTAGES = 0 # % нижней части экрана для служебных кнопок(запуск программы и т.д.)
FREESPACE_Y = (FREESPACE_Y_PERCENTAGES * SCREENHEIGHT)/100 # % нижней части экрана для служебных кнопок(запуск программы и т.д.)
SCREEN = pygame.display.set_mode((SCREENWIDTH,SCREENHEIGHT),)
pygame.display.set_caption("Conway's Game of Life")
SCREEN.fill(GREY)

CELLSIZE = 15 # размер одной квадратной ячейки
SEP = 1 # разделитель между ячейками
NUMofCOLUMN = int(SCREENWIDTH/(CELLSIZE + SEP)) # количество столбцов. Округление в меньшую сторону
NUMofROW = int((SCREENHEIGHT-FREESPACE_Y)/(CELLSIZE + SEP)) # количество строк. Округление в меньшую сторону
START_X = 0
START_Y = 0
END_X = START_X + (NUMofCOLUMN*(CELLSIZE+SEP)) - SEP # крайняя точка X поля 
END_Y = START_Y + (NUMofROW*(CELLSIZE+SEP)) - SEP # крайняя точка Y поля

'''----------------------------------------Блок с функциями-----------------------------------------------'''

# Получаем список кортежей координат верхней левой точки всех ячеек с учетом разделителя SEP
def getCellsCoordinates(startX, startY, cellsize, sep, numofcolumn, numofrow):
    initialX = startX
    initialY = startY
    cellcoordinate = []
    for row in range(numofrow):
        for column in range(numofcolumn):
            cellcoordinate.append([startX, startY, cellsize,cellsize])
            startX = startX+(cellsize+sep)
        startY = startY+(cellsize+sep)
        startX = initialX # возвращаем x к изначальному состоянию для перехода к новой строке.
    return cellcoordinate

# По координатам произвольной точки получаем кортеж координат верхней левой точки ячейки, в которой находится произвольная точка 
# вход: координаты верхней левой точки всех ячеек, положение X произвольной точки , положение Y произвольной точки, размер ячейки
def getTopLeftOfCell (coordinateList, x,y, cellsize=CELLSIZE): 
    for coordinate in coordinateList: 
        if (x >= coordinate[0]) and (x <= (coordinate[0] + cellsize)):
            cellX = coordinate[0]
        if (y>= coordinate[1]) and (y <=(coordinate[1] + cellsize)):
            cellY = coordinate[1]
    leftTop = (cellX, cellY, cellsize)
    return leftTop

# Метод для отрисовки живой ячейки
def reviveCell(surf,*cellXYSize,color=BLACK): # передаем surf, x, y, cellsize, цвет для живой ячейки
    cellX,cellY,cellSize = cellXYSize[0] # т.к. *cellXYSize создает кортеж из переданных элементов. Т.о. получаем корьеж кортежей. 
    return pygame.draw.rect(surf, color, (cellX, cellY, cellSize, cellSize))
    
# Метод для отрисовки мертвой ячейки
def killCell(surf,*cellXYSize,color=WHITE): # передаем surf, x, y, cellsize, цвет для мертвой ячейки
    cellX,cellY,cellSize = cellXYSize[0] # т.к. *cellXYSize создает кортеж из переданных элементов. Т.о. получаем корьеж кортежей. 
    return pygame.draw.rect(surf, color, (cellX, cellY, cellSize, cellSize))

# Выставляем состояние мертвый/живой. Если живой - добавляем в лист. Если мертвый и был в листе - удаляем из листа.
def setToAliveOrDeadState(state,x,y,listOfAliveCells):
    if state == 'ALIVE':
        if (x,y) in listOfAliveCells:
            return listOfAliveCells
        else:
            listOfAliveCells.append((x,y))
            return listOfAliveCells
    elif state == 'DEAD':
        if listOfAliveCells == []:
            return listOfAliveCells
        else:
            listOfAliveCells.remove((x,y))
            return listOfAliveCells

def isCellAlive(cellX,cellY,listOfAliveCells):
    if ((cellX, cellY)) in listOfAliveCells:
        return True
    else:
        return False

# Находим верхнии левые координаты соседних ячеек живой ячейки
def findMyNeighbors(topLeftX,topLeftY,cellsize=CELLSIZE, sep=SEP):
    x = topLeftX
    y = topLeftY
    step = cellsize + sep
    listOfNeighbors = [(x-step,y-step), (x,y-step), (x+step, y-step), # верхний ряд соседей
                        (x-step,y), (x+step,y), # средний ряд соседей
                        (x-step,y+step), (x,y+step), (x+step,y+step)] # нижний ряд соседей
    for val in range(len(listOfNeighbors)):
        coord_X = listOfNeighbors[val][0]
        coord_Y = listOfNeighbors[val][1]
        if ((coord_X < START_X ) and (coord_Y < START_Y)):
            listOfNeighbors[val] = (END_X-cellsize,END_Y-cellsize)
        elif ((coord_X > END_X ) and (coord_Y > END_Y)):
            listOfNeighbors[val] = (START_X,START_Y)
        elif (coord_X < START_X):
            listOfNeighbors[val] = (END_X-cellsize, coord_Y)
        elif (coord_X > END_X):
            listOfNeighbors[val] = (START_X, coord_Y)
        elif (coord_Y < START_Y):
            listOfNeighbors[val] = (coord_X, END_Y-cellsize)
        elif (coord_Y > END_Y):
            listOfNeighbors[val] = (coord_X, START_Y)
    return listOfNeighbors

def willCellDie(x,y,listOfAliveCells):
    listOfNeighbors = findMyNeighbors(x,y)
    aliveNeighborCount = 0
    deadNeighborCount = 0
    for neighbor in listOfNeighbors:
        if isCellAlive(neighbor[0], neighbor[1], listOfAliveCells):
            aliveNeighborCount += 1
        else:
            deadNeighborCount += 1
    if (aliveNeighborCount) < 2 or (aliveNeighborCount > 3):
        return True
    else:
        return False
            
def willNeighborBeAlive(neighbor_x, neighbor_y, listOfAliveCells):
    listofNeighbors = findMyNeighbors(neighbor_x,neighbor_y)
    aliveNeighborCount = 0
    for neighbor in listofNeighbors:
        if isCellAlive(neighbor[0],neighbor[1],listOfAliveCells):
            aliveNeighborCount += 1
    if aliveNeighborCount == 3:
        return True
    else:
        return False

def lifeCircle (listOfAliveCells):
    goingToListOfAliveCell = []
    goingFromListOfAliveCell = []
    for aliveCell in listOfAliveCells:
        aliveCell_X = aliveCell[0]
        aliveCell_Y = aliveCell[1]
        if willCellDie(aliveCell_X,aliveCell_Y,listOfAliveCells):
            goingFromListOfAliveCell.append((aliveCell_X,aliveCell_Y))
        else:
            pass
        listOfNeighbors = findMyNeighbors(aliveCell_X,aliveCell_Y)
        for neighbor in listOfNeighbors:
                neighbor_X = neighbor[0]
                neighbor_Y = neighbor[1]
                if willNeighborBeAlive (neighbor_X, neighbor_Y, listOfAliveCells):
                    if goingToListOfAliveCell.count((neighbor_X,neighbor_Y)) == 1: # иначе будут повторения в листе goingToListOfAliveCell от каждого живого соседа
                        pass
                    else:
                        goingToListOfAliveCell.append((neighbor_X,neighbor_Y))
    for dead in goingFromListOfAliveCell:
        dead_X = dead[0]
        dead_Y = dead[1]
        setToAliveOrDeadState('DEAD',dead_X,dead_Y,listOfAliveCells)
        #listOfAliveCells.remove(dead)
    
    for alive in goingToListOfAliveCell:
        alive_X = alive[0]
        alive_Y = alive[1]
        setToAliveOrDeadState('ALIVE',alive_X,alive_Y, listOfAliveCells)
        

'''----------------------------------------Конец блока с функциями-----------------------------------------'''  

cells = getCellsCoordinates(START_X,START_Y,CELLSIZE,SEP,NUMofCOLUMN,NUMofROW)
for cell in cells:
    pygame.draw.rect(SCREEN,WHITE,cell) # создаем поле
listOfAliveCells = []  
#log = open('logs.txt', 'w') 
prepearing = True
running = False
while prepearing:
    for event in pygame.event.get():
        if event.type == QUIT:
            prepearing = False
        elif event.type == MOUSEBUTTONDOWN: 
            mouseX, mouseY = pygame.mouse.get_pos()
            clickedCell = getTopLeftOfCell(cells, mouseX, mouseY, CELLSIZE)# находим верхнюю левую координату ячейки
            clicked_X, clicked_Y = clickedCell[0:2] 
            if isCellAlive(clicked_X, clicked_Y, listOfAliveCells):
                setToAliveOrDeadState('DEAD', clicked_X, clicked_Y, listOfAliveCells)
                killCell(SCREEN, clickedCell)
            else:
                setToAliveOrDeadState('ALIVE', clicked_X, clicked_Y, listOfAliveCells)
                reviveCell(SCREEN, clickedCell)
        elif event.type == KEYDOWN:
            if pygame.key.get_pressed()[K_RETURN]:
                prepearing = False
                running = True

    pygame.display.update()
    FPSCLOCK.tick(30*FPS/FPS)

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            prepearing = False
        if event.type == KEYDOWN:
            if pygame.key.get_pressed()[K_BACKSPACE]:
                running = False
                prepearing = True
    
    lifeCircle(listOfAliveCells)
    #log.write('AliveCell>>' + str(listOfAliveCells) + '\n')
    for cell in cells:
        if tuple(cell[0:2]) in listOfAliveCells:
            reviveCell(SCREEN,cell[0:3])
        else:
            killCell(SCREEN,cell[0:3])

    pygame.display.update()
    FPSCLOCK.tick(FPS) 

