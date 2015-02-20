import random
import threading
from tile import Tile
from plate import Plate

class World:
    def __init__(self, xsize = 600, ysize = 600, plateSize = 200, threads = 4, numPlates = 7):
        self.xSize = xsize
        self.ySize = ysize
        self.plateSize = plateSize
        self.tiles = {}
        self.plates = []
        self.threads = threads
        self.threadranges = []
        self.numPlates = numPlates


        for x in range(0, self.threads):
            r = [int(self.xSize / threads * x), int(self.xSize / threads * (x + 1))]
            self.threadranges.append(r)

        self.genWorld()

    def genTiles(self):
        for x in range(0, self.xSize):
            for y in range(0, self.ySize):
                elev = 1
                self.tiles[(x, y)] = Tile(x, y, self, elev)

    def genPlates(self):
        #Select seed tiles for plates
        for i in range(0, self.numPlates):
            seed = (round(random.random() * self.xSize), round(random.random() * self.ySize))
            plate = Plate([self.tiles[seed]], self)
            self.tiles[seed].plate = plate
            self.plates.append(plate)

        #Populate plates with tiles
        for a in range(1, self.xSize):
            for p in self.plates:
                t = p.tiles[0]
                for x in range(t.x - a, t.x + a + 1):
                    for y in range(t.y - a, t.y + a + 1):
                        if x < 0:
                            continue
                        elif x >= self.xSize:
                            continue
                        elif y < 0:
                            continue
                        elif y >= self.ySize:
                            continue

                        ti = self.tiles[(x, y)]
                        if not ti.plate:
                            ti.plate = p
                            p.tiles.append(ti)

        #Generate movement vectors for the plates
        for p in self.plates:
            p.moveVec = [random.random(), random.random()]
            pMag = (p.moveVec[0]**2 + p.moveVec[1]**2)**.5
            if pMag > 1:
                p.moveVec = [p.moveVec[0] / pMag, p.moveVec[1] / pMag]

        #Apply movement vector to tiles of the plates
        for p in self.plates:
            p.applyPlateMovement()


        """xplates = int(self.xSize / self.plateSize)
        yplates = int(self.ySize / self.plateSize)

        for xp in range(0, xplates):
            for yp in range(0, yplates):
                vec = [random.random() - .5, random.random() - .5]

                for x in range(xp * self.plateSize, (xp + 1) * self.plateSize):
                    for y in range(yp * self.plateSize, (yp + 1) * self.plateSize):
                        if x > self.xSize:
                            break
                        if y > self.ySize:
                            break

                        t = self.tiles[(x, y)]
                        t.moveVec[0] = vec[0] + (random.random() * .0001)
                        t.moveVec[1] = vec[1] + (random.random() * .0001)"""

    def findNeighbors(self):
        for x in range(0, self.xSize):
            for y in range(0, self.ySize):
                t = self.tiles[(x, y)]
                for a in range(x - 1, x + 2):
                    for b in range(y - 1, y + 2):
                        if a >= self.xSize:
                            continue
                            #a = 0
                        if b >= self.ySize:
                            continue
                            #b = 0
                        if a < 0:
                            continue
                            #a = self.xSize - 1
                        if b < 0:
                            continue
                            #b = self.ySize - 1

                        if self.tiles[(a, b)] != t:
                            t.neighbors.append(self.tiles[(a, b)])

    def calcForceBuffs(self, start, end):
        """Calculate the movement vectors for all tiles"""
        for x in range(start, end):
            for y in range(0, self.ySize):
                t = self.tiles[(x, y)]
                t.calcForceBuff()

    def threadCalcForceBuffs(self, thread):
        start = self.threadranges[thread][0]
        end = self.threadranges[thread][1]
        self.calcForceBuffs(start, end)

    def applyForceBuffs(self, start, end):
        """Apply the force buffers to the movement buffer"""
        for x in range(start, end):
            for y in range(0, self.ySize):
                t = self.tiles[(x, y)]
                t.applyForceBuff()

    def threadApplyForceBuffs(self, thread):
        start = self.threadranges[thread][0]
        end = self.threadranges[thread][1]
        self.applyForceBuffs(start, end)

    def applyMoveVecs(self, start, end):
        """Apply the movement vecotrs for all tiles"""
        for x in range(start, end):
            for y in range(0, self.ySize):
                t = self.tiles[(x, y)]
                t.applyMoveBuff()

    def threadApplyMoveVecs(self, thread):
        start = self.threadranges[thread][0]
        end = self.threadranges[thread][1]
        self.applyMoveVecs(start, end)

    def moveTiles(self, start, end):
        """Move all the tiles according to their movement vectors"""
        for x in range(start, end):
            for y in range(0, self.ySize):
                t = self.tiles[(x, y)]
                t.move()

    def threadMoveTiles(self, thread):
        start = self.threadranges[thread][0]
        end = self.threadranges[thread][1]
        self.moveTiles(start, end)

    def calcMassBuffs(self, start, end):
        """Calculate mass transfers among tiles based on relative distances"""
        for x in range(start, end):
            for y in range(0, self.ySize):
                t = self.tiles[(x, y)]
                t.calcMassTransfer()

    def threadCalcMassBuffs(self, thread):
        start = self.threadranges[thread][0]
        end = self.threadranges[thread][1]
        self.calcMassBuffs(start, end)

    def applyMassTransfers(self, start, end):
        """Apply mass tranfers in tiles"""
        for x in range(start, end):
            for y in range(0, self.ySize):
                t = self.tiles[(x, y)]
                t.applyMassTransfer()

    def threadApplyMassTransfers(self, thread):
        start = self.threadranges[thread][0]
        end = self.threadranges[thread][1]
        self.applyMassTransfers(start, end)

    def resetTilesPos(self, start, end):
        """Reset all the tiles to their default positions"""
        for x in range(start, end):
            for y in range(0, self.ySize):
                t = self.tiles[(x, y)]
                t.resetPos()

    def threadResetTilesPos(self, thread):
        start = self.threadranges[thread][0]
        end = self.threadranges[thread][1]
        self.resetTilesPos(start, end)

    def genWorld(self):
        """Generates the initial settings of a world"""
        print("Generating Tiles...")
        self.genTiles()
        print("Linking Tiles...")
        self.findNeighbors()
        print("Generating Plates...")
        self.genPlates()
        print("Inital world generation complete")

    def stepTectonics(self, steps = 1):
        """Step the tectonics of the world"""
        print("Stepping the world for", steps, "steps.")
        for x in range(0, steps):
            print('Step', x, 'of', steps, '.')
            print("Calculating force buffers...")
            self.calcForceBuffs(0, self.xSize)
            print("Applying force buffers...")
            self.applyForceBuffs(0, self.xSize)
            print("Applying move buffers...")
            self.applyMoveVecs(0, self.xSize)
            print("Moving tiles...")
            self.moveTiles(0, self.xSize)
            print("Calculating mass transfers...")
            self.calcMassBuffs(0, self.xSize)
            print("Applying mass transfers...")
            self.applyMassTransfers(0, self.xSize)
            print("Resetting tile positions...")
            self.resetTilesPos(0, self.xSize)
            print("Tile tectonics simulation advanced.")

    def threadStepTectonics(self, steps = 1):
        """Step the tectonics in multithreads"""
        print("Stepping the world for", steps, "steps.")

        

        print("Calculating force buffers")
        #Create our thread list
        tl = []
        for x in range(0, self.threads):
            tl.append(threading.Thread(target=self.threadCalcForceBuffs, args=[x]))

        for x in range(0, self.threads):
            tl[x].start()

        for x in range(0, self.threads):
            tl[x].join()

        print("Applying force buffers")
        #Create our thread list
        tl = []
        for x in range(0, self.threads):
            tl.append(threading.Thread(target=self.threadApplyForceBuffs, args=[x]))

        for x in range(0, self.threads):
            tl[x].start()

        for x in range(0, self.threads):
            tl[x].join()

        print("Applying movement vectors...")

        tl = []
        for x in range(0, self.threads):
            tl.append(threading.Thread(target=self.threadApplyMoveVecs, args=[x]))

        for x in range(0, self.threads):
            tl[x].start()

        for x in range(0, self.threads):
            tl[x].join()

        print("Moving tiles...")

        tl = []
        for x in range(0, self.threads):
            tl.append(threading.Thread(target=self.threadMoveTiles, args=[x]))

        for x in range(0, self.threads):
            tl[x].start()

        for x in range(0, self.threads):
            tl[x].join()

        print("Calculating mass transfers...")

        tl = []
        for x in range(0, self.threads):
            tl.append(threading.Thread(target=self.threadCalcMassBuffs, args=[x]))

        for x in range(0, self.threads):
            tl[x].start()

        for x in range(0, self.threads):
            tl[x].join()

        print("Applying mass transfers...")

        tl = []
        for x in range(0, self.threads):
            tl.append(threading.Thread(target=self.threadApplyMassTransfers, args=[x]))

        for x in range(0, self.threads):
            tl[x].start()

        for x in range(0, self.threads):
            tl[x].join()

        print("Resetting tile positions...")

        tl = []
        for x in range(0, self.threads):
            tl.append(threading.Thread(target=self.threadResetTilesPos, args=[x]))

        for x in range(0, self.threads):
            tl[x].start()

        for x in range(0, self.threads):
            tl[x].join()

        print("Tiles tectonics simulation advanced.")