import random

class Tile:
    def __init__(self, x, y, world, elevation):
        self.id = random.random() * 1000000000000000000000000000
        #The fixed space this tile occupies
        self.trux = x
        self.truy = y
        #The location of the tile before being reset to true position
        self.x = x
        self.y = y
        self.plate = None
        self.elevation = elevation
        self.neighbors = []
        self.moveVec = [0, 0]
        self.moveBuff = [0, 0]
        self.massBuff = {}
        self.forceBuff = []
        self.world = world

    def calcForceBuff(self):
        """Calculate the force buffer"""

        def dot(vec1, vec2):
            d = vec1[0] * vec2[0] + vec1[1] * vec2[1]
            return d

        def mag(vec):
            m = (vec[0]**2 + vec[1]**2)**.5
            return m

        def norm(vec):
            m = mag(vec)
            n = [vec[0] / m, vec[1] / m]
            return n

        def proj(vec1, vec2):
            """Project vec1 onto vec2"""
            unit = norm(vec2)
            scalar = mag(vec1)
            proj = [scalar * unit[0], scalar * unit[1]]
            return proj

        #Total momentum of the tile and neighboring tiles
        xP = 0
        yP = 0

        for n in self.neighbors:
            #Calculate the unit vector from the neighbor to the tile
            dirVec = [self.x - n.x, self.y - n.y]
            unitVec = norm(dirVec)

            #Find velocity from neighbor to tile
            toTile = proj(n.moveVec, unitVec)

            #Find velocity from tile to neighbor
            toNeighbor = proj(self.moveVec, unitVec)

            #Find relative velocity
            relVec = [0, 0]
            relVec[0] = toTile[0] - toNeighbor[0]
            relVec[1] = toTile[1] - toNeighbor[1]

            #If movement vectors are identical than no forces will be imparted.
            if mag(relVec) == 0:
                continue

            force = [0, 0]

            #Determine if the neighbor is moving away, toward, or neither.
            if relVec[0] <= 0 and relVec[1] <= 0:
                if mag(dirVec) > self.world.xSize / 2:
                    
                    #We are an edge case
                    relVec[0] = relVec[0] * -1
                    relVec[1] = relVec[1] * -1

                    #F = P/t, so F = elevation * relvec / 1 step
                    fmag = mag(relVec) * n.elevation
                    force[0] = fmag * unitVec[0]
                    force[1] = fmag * unitVec[1]

                    self.forceBuff.append(force)

                    #Apply Newton's third law
                    rForce = [force[0] * -1.0, force[1] * -1.0]
                    n.forceBuff.append(rForce)

                continue

            #F = P/t, so F = elevation * relvec / 1 step
            fmag = mag(relVec) * n.elevation
            force[0] = fmag * unitVec[0]
            force[1] = fmag * unitVec[1]

            self.forceBuff.append(force)

            #Apply Newton's third law
            rForce = [force[0] * -1.0, force[1] * -1.0]
            n.forceBuff.append(rForce)

            #Find vector perpendicular to the normal force
            perp = [-force[1], force[0]]
            uPerp = norm(perp)

            fricVec = proj(n.moveVec, uPerp)

            if ((uPerp[0] < 0 and fricVec[0] < 0) or 
                (uPerp[0] > 0 and fricVec[0] > 0) or 
                (uPerp[1] < 0 and fricVec[1] < 0) or 
                (uPerp[1] > 0 and fricVec[1] > 0)):
                uPerp[0] = uPerp[0] * -1
                uPerp[1] = uPerp[1] * -1


            #Now calculate friction force
            #Ff <= uFn
            friction = .4 * mag(force)

            fricVec = [friction * uPerp[0], friction * uPerp[1]]

            n.forceBuff.append(fricVec)
            rFriction = [fricVec[0] * -1, fricVec[1] * -1]
            self.forceBuff.append(rFriction)



            #xP += relVec[0] * n.elevation
            #yP += relVec[1] * n.elevation

        #xP += self.moveVec[0] * self.elevation
        #yP += self.moveVec[1] * self.elevation

        #Some momentum is lost in the collisions
        #xP = xP * .9
        #yP = yP * .9

        #xv = xP / self.elevation
        #yv = yP / self.elevation

        #mag = (xv**2 + yv**2)**.5
        #if mag > 1:
        #    xv = xv / mag
        #    yv = yv / mag

        #self.moveBuff = [xv, yv]

            # if forcedot < 0:
            #     #If dot product is negative than it is moving away from the tile and not importing a resisting force
            #     continue


            
            

            # fmag = (relVec[0]**2 + relVec[1]**2)**.5 * n.elevation


            # # try:
            # #     force[0] = n.elevation * relVec[0]
            # #     force[1] = n.elevation * relVec[1]
            # # except:
            # #     print('directVec', dirVec)
            # #     print('Forcedot', forcedot)
            # #     print('self moveVec', self.moveVec)
            # #     print('ForceVec:', '<', forceVec[0], ',', forceVec[1], '>')
            # #     print('n.elevation', n.elevation)



           
            # if mag != 0:
            #     uPerp = [perp[0] / mag, perp[1] / mag]
            #     if (perp[0] < 0 and n.moveVec[0] < 0) or (perp[0] > 0 and n.moveVec[0] > 0) or (perp[1] < 0 and n.moveVec[1] < 0) or (perp[1] > 0 and n.moveVec[1] > 0):
            #         perp[0] = perp[0] * -1
            #         perp[1] = perp[1] * -1

            

            

            


    def applyForceBuff(self):
        """Apply the forces in the force buffer to the movement buffer"""
        if not self.forceBuff:
            #No forces are being imparted
            self.moveBuff = self.moveVec
            self.forceBuff = []
            return
        else:
            sumForce = [0, 0]
            for f in self.forceBuff:
                sumForce[0] += f[0]
                sumForce[1] += f[1]

            #F=ma, so a = F/m
            acceleration = [sumForce[0] / self.elevation, sumForce[1] / self.elevation]
            self.moveBuff = [self.moveVec[0] + acceleration[0], self.moveVec[1] + acceleration[1]]
            mag = (self.moveBuff[0]**2 + self.moveBuff[1]**2)**.5
            if mag > 1:
                #Calculate new unit vector
                self.moveBuff[0] = self.moveBuff[0] / mag
                self.moveBuff[1] = self.moveBuff[1] / mag

            #Clear the force buffer
            self.forceBuff = []


    def applyMoveBuff(self):
        """Move the movement buffer into the movement vector"""
        self.moveVec[0] = self.moveBuff[0]
        self.moveVec[1] = self.moveBuff[1]

    def move(self):
        """Alter the coordinates of the tiles based on the movement vector"""
        self.x += self.moveVec[0]
        self.y += self.moveVec[1]

        """if self.x < 0:
            self.x = self.world.xSize - 1
        if self.x > self.world.xSize:
            self.x = 0
        if self.y < 0:
            self.y = self.world.ySize - 1
        if self.y > self.world.ySize:
            self.y = 0"""

    def calcMassTransfer(self):
        """Calculate mass to be transferred based on relative distances"""
        for n in self.neighbors:
            dirVec = [self.x - n.trux, self.y - n.truy]
            mag = (dirVec[0]**2 + dirVec[1]**2)**.5

            truDirVec = [self.trux - n.trux, self.truy - n.truy]
            truMag = (truDirVec[0]**2 + truDirVec[1]**2)**.5

            displacement = truMag - mag

            if truMag > self.world.xSize / 2:
                proportion = displacement * -1
                self.massBuff[(n.trux, n.truy)] = self.elevation * proportion
                continue

            if displacement <= 0:
                continue

            proportion = displacement / truMag

            self.massBuff[(n.trux, n.truy)] = self.elevation * proportion

    def applyMassTransfer(self):
        """Apply the mass transfers to neighbors in the mass buffer"""
        
        if self.trux == 0 or self.truy == 0 or self.trux == self.world.xSize - 1 or self.truy == self.world.ySize - 1:
            self.elevation = self.elevation * .25
            return

        for n in self.neighbors:
            if n.elevation >= 50:
                self.massBuff[(n.trux, n.truy)] = 0
                continue

            if (n.trux, n.truy) in self.massBuff:
                n.elevation += self.massBuff[(n.trux, n.truy)] * .75
                self.elevation -= self.massBuff[(n.trux, n.truy)] * .75

                if n.elevation > 50:
                    n.elevation = 50

                if self.elevation < .01:
                    self.elevation = .01

                    
                self.massBuff[(n.trux, n.truy)] = 0

        #self.massBuff = {}

    def resetPos(self):
        self.x = self.trux
        self.y = self.truy




