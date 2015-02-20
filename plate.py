class Plate:
	def __init__(self, tiles, world):
		"""A polygonal plate that moves across the surface of the world over large timescales"""
		self.tiles = tiles
		if not tiles:
			self.tiles = []
		self.world = world
		self.moveVec = [0, 0]
		self.moveBuff = [0, 0]
		self.forceBuff = [0, 0]
		self.mass = 0

	

	def calcPlateForceBuff(self):
		"""Calculates the total force being applied on the plate"""
		for t in self.tiles:
			#Determine if tile is on the edge of the plate
			edge = False
			for n in t.neighbors:
				if n.plate != self:
					edge = True

			if edge:
				t.calcForceBuff()
				self.forceBuff[0] += t.forceBuff[0]
				self.forceBuff[1] += t.forceBuff[1]

	def applyPlateForceBuff(self):
		"""Applies the force buffer onto the plate"""
		self.mass = 0
		for t in self.tiles:
			self.mass += t.elevation

		#F = m/a so a = f/m
		acceleration = [0, 0]
		acceleration[0] = self.forceBuff[0] / self.mass
		acceleration[1] = self.forceBuff[1] / self.mass

		self.moveBuff[0] += acceleration[0]
		self.moveBuff[1] += acceleration[1]

		mMag = (self.moveBuff[0]**2 + self.moveBuff[1]**2)**.5
		if mMag > 1:
			self.moveBuff[0] = self.moveBuff[0] / mMag
			self.moveBuff[1] = self.moveBuff[1] / mMag

	def applyPlateMoveBuff(self):
		"""Applies the movement buffer onto the plate"""
		self.moveVec[0] = self.moveBuff[0]
		self.moveVec[1] = self.moveBuff[1]

	def applyPlateMovement(self):
		"""Applies the movement vector of the plate to all of its tiles"""
		for t in self.tiles:
			t.moveVec[0] = self.moveVec[0]
			t.moveVec[1] = self.moveVec[1]

	def movePlateTiles(self):
		"""Moves all the plates in the tile"""
		for t in self.tiles:
			t.move()
