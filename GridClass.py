class Grid(object):

	def __init__(self, LARG, HAUT, nbCols, nbLigs, offsetX=0, offsetY=0, cacheFullGrid=False):
		#cacheFullGrid crée un dict des traduction d'indexes vers coords de grid.

		self.LARG_ = LARG
		self.HAUT_ = HAUT
		self.nbCols_ = int(nbCols)
		self.nbLigs_ = int(nbLigs)

		self.offsetX_ = offsetX
		self.offsetY_ = offsetY

		self.rangeX = ()
		self.rangeY = ()

		self.cacheON = cacheFullGrid

		self.GridCoords = []
		self.GridDict = dict()

		self.CellHAUT = 0
		self.CellLARG = 0
		self.GridMaker()

	def __str__(self):
		return ''.join([str(lig)+'\n' for lig in self.GridCoords])
		
	def GridMaker(self):

		self.CellLARG = self.LARG_ / self.nbCols_
		self.CellHAUT = self.HAUT_ / self.nbLigs_
		minX, minY = float('inf'), float('inf')
		maxX, maxY = -float('inf'), -float('inf')
		for ligne in range(self.nbLigs_ + 1):
			ligneArr = []
			for col in range(self.nbCols_ + 1):
				newX = col * self.CellLARG + self.offsetX_
				newY = ligne * self.CellHAUT + self.offsetY_

				if newX > maxX: maxX = newX
				if newX < minX: minX = newX
				if newY > maxY: maxY = newY
				if newY < minY: minY = newY

				ligneArr += [(newX, newY)]
				
				if self.cacheON:
					self.GridDict[(col, ligne): (newX, newY)]

			self.GridCoords += [ligneArr]

		self.rangeX = (minX, maxX)
		self.rangeY = (minY, maxY)

	def __str__(self):
		return ''.join([str(lig)+'\n' for lig in self.GridCoords])

	def __getitem__(self, index):
		return self.GridCoords[index]

	def __len__(self):
		return len(self.GridCoords)

	def is_inbound(self, coord):
		#Bool teste si la coord est à l'inérieur des limites de l'instance Grid.
		
		LARG_test = self.offsetX_ <= coord[0] <= self.LARG_ + self.offsetX_
		HAUT_test = self.offsetY_ <= coord[1] <= self.HAUT_ + self.offsetY_
		return LARG_test or HAUT_test
		

	def find_coord(self, indexes):
		# Trouve la coord nord-ouest de la cellule aux indexes de grid (x,y)
		if self.cacheON:	return self.GridDict[tuple(indexes)]
		else:				return self.GridCoords[indexes[1]][indexes[0]]

	def find_bboxIDX(self, indexes):
		# Même que find_bboxCoord mais donne les indexes des 4 vertexes.
		cellNW = self.find_coord(indexes)
		ox, oy = cellNW[0], cellNW[1]
		cLARG = self.CellLARG
		cHAUT = self.CellHAUT
		return [cellNW, (ox + cLARG, oy), (ox + cLARG, oy + cHAUT), (ox, oy + cHAUT)]

	def find_bboxCoord(self, coord):
		#Avec une coordonnée donnée, trouve toutes les coordonnées de la cellule dans laquelle la coord se trouve.
		#coord : (x,y)

		if self.is_inbound(coord):
			cellID = self.find_cellIndex(coord)
			print(cellID)
			return self.find_bboxIDX(cellID)
		else:
			raise ValueError("La coord est hors limite.")

	def find_cellIndex(self, coord):
		#Avec une coordonnée donné, trouve la cellule dans laquelle la coord se trouve.
		#coord : (x,y)
		if self.is_inbound(coord):			
			return (coord[0] // self.CellLARG, coord[1] // self.CellHAUT)
		else:
			raise ValueError("La coord est hors limite.")

	def find_cellInfo(self,coord, indexes=()):
		if self.is_inbound(coord):
			return [self.find_cellIndex(coord), self.find_bboxCoord(coord)]
		else:
			raise ValueError("La coord est hors limite.")

'''
grid1 = Grid(100, 200, 10, 10)
print(grid1.HAUT_)

test_coord = (50,100)
for index, i in enumerate(grid1.GridCoords):
	print(grid1.GridCoords[index])
print(grid1.CellLARG, grid1.CellHAUT)
print(grid1.find_bboxCoord(test_coord))
print(grid1.find_cellInfo(test_coord))
'''