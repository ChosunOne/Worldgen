from world import World
import pygame
import os
import sys
from pygame.locals import *

class PyManMain:

    def __init__(self, width=200, height=200):
        pygame.init()
        self.fpsClock = pygame.time.Clock()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('WorldGen')
        self.red = pygame.Color(255, 0, 0)
        self.green = pygame.Color(0, 255, 0)
        self.blue = pygame.Color(0, 0, 255)
        self.fontObj = pygame.font.Font('freesansbold.ttf', 24)
        msg = 'WorldGen Initialized'
        self.mousex, self.mousey = (0, 0)
        self.msg = ''
        self.earth = World(xsize=100, ysize=100, plateSize = 100, threads = 8)
        self.viewMode = 1

    def MainLoop(self):
        clickX = 0
        clickY = 0
        timer = 0
        scale = round(self.width / self.earth.xSize)
        camPos = [0, 0]
        tiles = self.earth.tiles
        screen = self.screen
        w = self.width
        h = self.height


        screenArr = pygame.Surface((w, h))
        screen.fill(pygame.Color(0,0,0))

        while True:
            if timer > 10000:
                timer = 0

            if timer % 1 == 0:
                self.earth.threadStepTectonics()
                pass

            #screen.fill(pygame.Color(0,0,0))
            
            #screenArr = pygame.PixelArray(screen)
            
            if scale == 1:
                camPos = [0, 0]

            pLength = int(w / scale)
            pHeight = int(h / scale)

            if camPos[0] > w - pLength:
                camPos[0] = w - pLength
            if camPos[1] > h - pHeight:
                camPos[1] = h - pHeight

            preScreen = [[0 for x in range(0, pHeight)] for x in range(0, pLength)]

            for x in range(int(camPos[0]), int(pLength + camPos[0]), 1):
                for y in range(int(camPos[1]), int(pHeight + camPos[1]), 1):
                    a = int(x - camPos[0])
                    b = int(y - camPos[1])
                    #try:
                    rcol = 0
                    gcol = 0
                    bcol = 0
                    elev = 0

                    if self.viewMode == 0:
                        elev += round(tiles[(x, y)].elevation / 50 * 255)
                        rcol = elev
                        gcol = elev
                        bcol = elev
                    elif self.viewMode == 1:
                        #westbound x is red
                        if tiles[(x, y)].moveVec[0] < 0:
                            rcol += int(abs(tiles[(x, y)].moveVec[0] * 255))
                        #stationary x is black
                        #eastbound x is blue
                        elif tiles[(x, y)].moveVec[0] > 0:
                            bcol += int(abs(tiles[(x, y)].moveVec[0] * 255))

                        #southbound y is green 
                        if tiles[(x, y)].moveVec[1] > 0:
                            gcol += int(abs(tiles[(x, y)].moveVec[1] * 255))
                        #stationary y is black
                        #northbound y is purple
                        elif tiles[(x, y)].moveVec[1] < 0:
                            rcol += int(abs(tiles[(x, y)].moveVec[1] * 255))
                            bcol += int(abs(tiles[(x, y)].moveVec[1] * 255))

                    elif self.viewMode == 2:
                        elev += tiles[(x, y)].elevation
                        if elev > 50:
                            rcol = 255
                            gcol = 0
                            bcol = 0
                        elif elev < 0:
                            rcol = 0
                            bcol = 255
                            gcol = 0
                        elif elev < 8:
                            rcol = 0
                            gcol = 0
                            bcol = 255
                        elif elev < 20:
                            rcol = 0
                            gcol = 255
                        elif elev < 30:
                            rcol = 128
                            gcol = 64
                        elif elev <= 50:
                            rcol = 255
                            gcol = 255
                            bcol = 255
                        else:    
                            rcol += elev
                            gcol += rcol
                            bcol += rcol



                    if rcol > 255:
                        rcol = 255
                    if gcol > 255:
                        gcol = 255
                    if bcol > 255:
                        bcol = 255

                    try:
                        preScreen[a][b] = pygame.Color(rcol, gcol, bcol)
                    except:
                        print('Exception at:', a, b, 'and', x, y)
                        print(rcol, gcol, bcol)

            if timer % 1 == 0:
                for x in range(0, pLength):
                    for y in range(0, pHeight):
                        for a in range(x * scale, (x * scale) + scale):
                            for b in range(y * scale, (y * scale) + scale):
                                screenArr.set_at((a , b), preScreen[x][y])

            #del screenArr
            screen.blit(screenArr, (0, 0))

            msgSurfaceObj = self.fontObj.render(self.msg, False, self.red)
            msgRectObj = msgSurfaceObj.get_rect()
            msgRectObj.topleft = (clickX, clickY)
            screen.blit(msgSurfaceObj, msgRectObj)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONUP:
                    clickX, clickY = event.pos
                    t = tiles[(int(camPos[0] + clickX/scale),int(camPos[1] + clickY/scale))]
                    if event.button == 1:
                        #Left Click
                        print('Elevation:', str(t.elevation))
                        print('Move Vector:', '(', str(t.moveVec[0]), ',', str(t.moveVec[1]), ')')
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        self.earth.stepTectonics(steps = 1)
                    elif event.key == K_t:
                        self.earth.stepTectonics(steps = 10)
                    elif event.key == K_m:
                        self.viewMode = 2
                    elif event.key == K_v:
                        self.viewMode = 1
                    elif event.key == K_e:
                        self.viewMode = 0
                    elif event.key == K_LEFT:
                        camPos[0] -= 10
                        if camPos[0] < 0:
                            camPos[0] = 0
                    elif event.key == K_RIGHT:
                        camPos[0] += 10
                        if camPos[0] > self.width - self.width / scale:
                            camPos[0] = self.width - self.width / scale
                    elif event.key == K_UP:
                        camPos[1] -= 10
                        if camPos[1] < 0:
                            camPos[1] = 0
                    elif event.key == K_DOWN:
                        camPos[1] += 10
                        if camPos[1] > self.height - self.height / scale:
                            camPos[1] = self.height - self.height / scale
                    elif event.key == K_LSHIFT:
                        scale += 1
                    elif event.key == K_LCTRL:
                        scale -= 1
                        if scale < 1:
                            scale = 1

            pygame.display.update()
            self.fpsClock.tick(30)
            timer += 1


if __name__ == "__main__":
    MainWindow = PyManMain()
    MainWindow.MainLoop()