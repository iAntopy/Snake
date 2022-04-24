from random import randint as rint, choice
from math import ceil
from time import time

import config

print('Ouverture du module PowerUps :', config.snakeGame)

class PowerUps_class:
	can = config.master_
	grid = config.grid_
	Game = config.snakeGame
	#print('config import de PowerUps_class :',can, grid, Game)
	
	#print('can :', can, 'grid :', grid, 'Game :', Game)

		
	# Dict des objets des PowerUps spécifique. Coord en keyword.
	PowerUp_instances =		dict()	

	PowerUp_onMap = False

	blinker_afterIDs = []	
	blinker_indictateur= {False: 'hidden', True: 'normal'}

	PowerUp_afterIDs = []

	# Pour tester si la coord d'un PowerUp est valide, liste d'appartenances à vérifier.
	usual_suspect = (Game.snake_peauMorte, Game.snake, PowerUp_instances)

	PowerUp_codes = ('Mu','Zi','Wp', 'Rm')
	PowerUp_chances = (0.4,0.3,0.2,0.1)

	PowerUp_Dict = {code:{'chance': chance, 'func': None} for code, chance in zip(PowerUp_codes, PowerUp_chances)}
	PowerUp_randPool = None

	scaledCoords = lambda self, r1, coord1, r2: ((coord1[0]*r2)/r1 , (coord1[1]*r2)/r1)
	hypot = lambda self, a,b: (a**2 + b**2)**(1/2)


	def __init__(self):

		PowerUp_funcs = (PowerUp_mue, PowerUp_zigzag, PowerUp_wrapAround, PowerUp_ram)
		[self.PowerUp_Dict[code].update({'func': func}) for code, func in zip(self.PowerUp_codes, PowerUp_funcs )]	#{'Mu': PowerUp_mue,'Zi': PowerUp_zigzag, 'Wp': PowerUp_wrapAround}
		
		
		# Crée une distribution des codes de PowerUps_class selon la proportion de leur chance d'appartion.
		# choisir un sample de 1 de cette distribution pour déterminer quel PowerUp créer.
		# Créé à l'ouverturre du jeu et jamais modifié ensuite.
		randPool = 	[]
		for code in self.PowerUp_Dict:
			chance = self.PowerUp_Dict[code]['chance']
			randPool += [code for i in range(int(10*chance))] 
		self.PowerUp_randPool = tuple(randPool)


		
	def __contains__(self, autre):
		return autre in self.PowerUp_instances


	def PowerUp_RESET(self):

		self.PowerUp_onMap = False		

		[self.PowerUp_wipe(inst) for inst in self.PowerUp_instances.copy()]

		self.can.delete('PowerUp')


	def PowerUp_GAMEOVER_Procedure(self):

		for ID in self.blinker_afterIDs+self.PowerUp_afterIDs:
			#print('afterID :',ID)
			try:
				self.can.after_cancel(ID)
			except:
				continue			

		self.blinker_afterIDs.clear()

		for inst in self.PowerUp_instances.values():
			[ self.can.itemconfig(item, fill='black', state='normal', outline= 'black') for item in inst['itemIDs']]
			[ self.can.after_cancel(after) for after in inst['func'].afterIDs]

			
		self.Game.têteOffset = [0,0]

	def espace_vide_check(self, coord):

		coord_valide = True
		for suspect in self.usual_suspect:	
			coord_valide &= (coord not in suspect)

		return coord_valide

	def PowerUp_Gen(self):

		# New Coord_		
		while True:
			tPow = (rint(0, self.grid.nbCols_-1), rint(0, self.grid.nbLigs_-1))
			
			if self.espace_vide_check(tPow): break	

		# _New Coord

		# New object_
		newPowerUp = self.PowerUp_Dict[choice( self.PowerUp_randPool) ]['func'](tPow)
		rim_coul = newPowerUp.rim_coul
		trig_coul = newPowerUp.trig_coul
		# _New object


		#self.PowerUps_coords += [tPow]
		self.PowerUp_onMap = True
		self.PowerUp_instances.update( {tPow: {'func': newPowerUp, 'itemIDs': []} } )


		# Shape_
		Shape_Base = (self.grid.find_coord(tPow), self.grid.find_coord((tPow[0]+1, tPow[1])))
		cL, cH = self.grid.CellLARG, self.grid.CellHAUT
		polyID = self.can.create_polygon(*Shape_Base[0], *Shape_Base[1], Shape_Base[0][0] + cL/2, Shape_Base[0][1] + cH, fill= trig_coul, tags='PowerUp')
		arcID  = self.can.create_oval(Shape_Base[0][0] - cL/2, Shape_Base[0][1] - cH/2,Shape_Base[0][0] + cL*1.5, Shape_Base[0][1] + cH*1.5
				,outline= rim_coul, width=2, tags='PowerUp')
		
		self.PowerUp_instances[tPow]['itemIDs'] += [polyID, arcID]
		# _Shape

		self.blinker_afterIDs += [self.can.after( newPowerUp.blinker_deleteTimer - newPowerUp.blinker_PanicTime, (lambda POW_obj, speed: lambda: self._Blinker(POW_obj, speed) )(newPowerUp, newPowerUp.blinker_speed) )]


		del tPow, Shape_Base


	def PowerUp_wipe(self, coord):

		# Suprime seulement la shape du PowerUp dans le tableau.
		#print('tête:',self.Game.tête)
		Power_inst =  self.PowerUp_instances.pop(coord)

		#print('powCoord :', Power_inst)
		try:
			[self.can.delete(item) for item in Power_inst['itemIDs']]			
		except ValueError:
			print('PowerUp déjà suprimé') 

		del Power_inst['func']

		if len(self.PowerUp_instances) == 0:
			#self.PowerUps_coords.remove(coord)
			self.PowerUp_onMap = False


	def _Blinker(self, POW_obj, speed):
		#print('GAME!!! ',self.Game)
		try:
			#print('coord:',coord, 'speed:', speed,'Instances :', self.PowerUp_instances)
			#POW = self.PowerUp_instances[coord]['func']

			POW_obj.blinker_on = not POW_obj.blinker_on
			POW_obj.blinker_counter -= 1
			[self.can.itemconfig(item, state= self.blinker_indictateur[POW_obj.blinker_on]) for item in self.PowerUp_instances[POW_obj.coord_]['itemIDs']]
						
		except KeyError:
			print('Binker tente de suprimer un PowerUp mort.')
			return None

		if not self.Game.GAMEOVER:
			if POW_obj.blinker_counter > 0:
				self.blinker_afterIDs += [self.can.after(speed, lambda: self._Blinker(POW_obj, speed))]
				#print(self.PowerUp_instances)
			else:
				self.PowerUp_wipe(POW_obj.coord_)
				#print(self.PowerUp_instances)

	def _GaugeManager(self, POW_obj):
		#print('GAUGE FEST !')
		Prop =  POW_obj.event_timer / POW_obj.eventDurée #1 - ((time() - POW_obj.eventStartTime) / POW_obj.eventDuréeSec)
		
		self.can.coords('Gauge1', self.Game.Gauge1Base[0], self.Game.emptyGaugePx_Y, self.Game.Gauge1Base[1], self.Game.emptyGaugePx_Y-(self.Game.fullGaugeLen * Prop) )

		if POW_obj.event_timer > 0:
			self.PowerUp_afterIDs += [self.can.after(self.Game.Gauge_updateRate, lambda: self._GaugeManager(POW_obj))]
			POW_obj.event_timer -= self.Game.Gauge_updateRate


class PowerUp_mue(PowerUps_class):
	def __init__(self, coord):

		self.coord_ = coord
		#self.Game = config.snakeGame
		self.eventActive = False
		self.score_bonus = 1000

		self.afterIDs = []

		self.blinker_deleteTimer = 10000 #ms

		self.blinker_on = False
		self.blinker_PanicTime = 3000 # ms avant la supression du PowerUp
		self.blinker_speed = 500
		self.blinker_counter = int(self.blinker_PanicTime / self.blinker_speed)

		self.rim_coul = 'red'
		self.trig_coul = 'light green'

	def activate(self):
		self.PowerUp_wipe(self.coord_)

		self.Game.combo_timer = self.Game.combo_delay
		self.Game.Score_addBonus(self.score_bonus)

		midCut = self.Game.longueur.get() / 2
		intMidCut = int(midCut)
		self.Game.longueur.set(ceil(midCut))

		# Crée un dict des peaux mortes avec coord en key et itemID en value
		for seg in range(intMidCut):
			val = self.Game.segmentsPool.pop(0)
			self.can.dtag(val, 'Snake')
			self.can.addtag_withtag('PeauMorte', val)
			#print('key :', key, 'val :', val)
			self.Game.snake_peauMorte[self.Game.snake.pop(0)] = val

		self.can.itemconfig('PeauMorte', fill='light grey')
		

class PowerUp_zigzag(PowerUps_class):
	def __init__(self, coord):

		self.coord_ = coord
		#self.POW = 0 # Placeholder pour self.PowerUp_instances[coord]['func']
		self.score_bonus = 2000
		self.score_mod = 4

		self.eventActive = False
		self.eventDurée = 5000 # ms
		self.event_timer = self.eventDurée
		self.afterIDs = []

		self.blinker_deleteTimer = 6000 #ms
		self.blinker_on = False
		self.blinker_PanicTime = 2000 # ms avant la supression du PowerUp
		self.blinker_speed = 100
		self.blinker_counter = int(self.blinker_PanicTime / self.blinker_speed)

		self.rim_coul = 'blue'
		self.trig_coul = 'yellow'

		# Preloads_
		self.ziggy = self.zigzagGen(8,7)
		self.after = self.can.after
		# _Preloads

	@staticmethod
	def zigzagGen(periode, seq_offset):
		# génère la sécance -1,0,0,1,1,0,0,-1, ...
		# Avec 3 bits 0,0,0 la première à droite étant une gate qui ouvre une fois sur deux,
		# la deuxième représentant la magnétude du multiplicateur, 0 ou 1,
		# et la troixième la polarité, 0 étant positif 1 étant négatif ( (-1)^Polarité == 1 si Pol == 0 et -1 si Pol == 1 ),
		# En multipliant la 2e et 3e bit à chaque fois qu'on ajoute 1 au nb binaire,
		# la magnétude changera à chaque 2 itérations, la polarité à chaque 4 itérations et le cycle durera 8 itérations.
		i = periode + seq_offset
		while True:
			Byte = '{0:03b}'.format( i )
			yield int(Byte[-2]) * (-1)**int(Byte[-3])
			i+=1

	
	def activate(self):
		print('ZIGZAG ACTIF !')

		self.eventStartTime = time()

		self.Game.combo_timer = self.Game.combo_delay
		self.Game.Score_addBonus(self.score_bonus)
		self.Game.score_modif.set(self.Game.score_modif.get() + self.score_mod)

		self.can.coords('Gauge1', self.Game.Gauge1Base[0], self.Game.emptyGaugePx_Y, self.Game.Gauge1Base[1], self.Game.emptyGaugePx_Y-self.Game.fullGaugeLen)
		self._GaugeManager(self.PowerUp_instances[self.coord_]['func'])

		self.PowerUp_wipe(self.coord_)
		self.afterIDs += [self.after(self.eventDurée, self.stop)]
		print('STOP EVENTID :', self.afterIDs[-1])
		
		self.can.itemconfig('frame', outline='yellow')
		self.eventActive = True
		
		self.anime()


	def stop(self):
		print('TIME TO STOP !!')
		self.eventActive = False

		for ID in self.afterIDs:
			try:				self.can.after_cancel(ID)
			except ValueError:	pass

		self.Game.têteOffset[0], self.Game.têteOffset[1] = (0,0)
		self.eventStartTime = 0

		self.can.itemconfig('frame', outline='light blue')
		self.can.coords('Gauge1', self.Game.Gauge1Base[0], self.Game.emptyGaugePx_Y, self.Game.Gauge1Base[1], self.Game.emptyGaugePx_Y)

		self.Game.score_modif.set(self.Game.score_modif.get() - self.score_mod)


	def anime(self):
		if self.Game.direction in self.Game.noGoodDirs[0]:
			# Voyage sur axe des 'Y'
			nextZig = next(self.ziggy)			
			self.Game.têteOffset[0] = nextZig
			
		else:
			# Voyage sur axe des 'X'
			nextZag =  next(self.ziggy)			
			self.Game.têteOffset[1] = nextZag
			

		if self.eventActive and not self.Game.GAMEOVER:
			self.afterIDs += [self.after(self.Game.vitesse_actuelle,  self.anime)]
			self.afterIDs.pop(0)



class PowerUp_wrapAround(PowerUps_class):
	def __init__(self, coord):
		# Permet de ne pas mourir en frappant les mures
		# et de revenir de l'autre côté du tableau à la pac-man/asteroid.
		self.coord_ = coord
		#self.POW = 0 # Placeholder pour self.PowerUp_instances[coord]['func']
	
		self.score_bonus = 5000
		self.eventActive = False
		self.eventDurée = 10000
		self.event_timer = self.eventDurée
		self.afterIDs = []
		self.extraMove = [(1,1), (1,-1), (-1,1), (-1,-1)]

		self.blinker_deleteTimer = 5000 #ms
		self.blinker_on = False
		self.blinker_PanicTime = 1000 # ms avant la supression du PowerUp
		self.blinker_speed = 100
		self.blinker_counter = int(self.blinker_PanicTime / self.blinker_speed)


		self.rim_coul = 'white'
		self.trig_coul = 'black'
		self.cL, self.cH = self.grid.CellLARG, self.grid.CellHAUT

		# Preloads_
		self.after = self.can.after
		self.after(1000, self.PowerUp_dance)

	def PowerUp_dance(self):

		#print('WrapGen  dance')
		print(self.PowerUp_instances)
		oldDictVals = self.PowerUp_instances.pop(self.coord_)
		itemIDs = oldDictVals['itemIDs']
		# New Coord_		
		while True:
			coord_valide = True
			move = choice(list(self.Game.dirDict.keys())+self.extraMove)			
			newCoord = (self.coord_[0]+move[0], self.coord_[1]+move[1])
			#print('\nmove :', move, 'newCoord :', newCoord)
				
			coord_valide &= self.espace_vide_check(newCoord)

			for condition in self.Game.failState_conditions[:2]:				
				coord_valide &= not condition(newCoord)

			if coord_valide: break	 
		#print('While Loop OVER !')
		# Shape_
		Shape_Base = (self.grid.find_coord(newCoord), self.grid.find_coord((newCoord[0]+1, newCoord[1])))
		self.can.coords(itemIDs[0], *Shape_Base[0], *Shape_Base[1], Shape_Base[0][0] + self.cL/2, Shape_Base[0][1] + self.cH)
		self.can.coords(itemIDs[1], Shape_Base[0][0] - self.cL/2, Shape_Base[0][1] - self.cH/2,Shape_Base[0][0] + self.cL*1.5, Shape_Base[0][1] + self.cH*1.5)
		# _Shape
		
		self.PowerUp_instances[newCoord] = oldDictVals
		self.coord_ = newCoord

		#print('Wrap Dance pre after !')
		if not self.eventActive and not self.Game.GAMEOVER:
			self.afterIDs += [self.after(500, self.PowerUp_dance)]


	def activate(self):
		print('WrapAround ACTIF !')
		self.eventActive = True

		self.eventStartTime = time()

		self.Game.combo_timer = self.Game.combo_delay
		self.Game.Score_addBonus(self.score_bonus)

		self.can.coords('Gauge1', self.Game.Gauge1Base[0], self.Game.emptyGaugePx_Y, self.Game.Gauge1Base[1], self.Game.emptyGaugePx_Y-self.Game.fullGaugeLen)
		self._GaugeManager(self.PowerUp_instances[self.coord_]['func'])

		self.PowerUp_wipe(self.coord_)
		self.afterIDs += [self.after(self.eventDurée, self.stop)]
		print('STOP EVENTID :', self.afterIDs[-1])
		
		self.can.itemconfig('frame', outline='yellow')
		

		self.Game.rawfilter = 'wrapAround'
		self.Game.failState_setup = (2,3)


	def stop(self):
		print('TIME TO STOP !!')

		self.Game.rawfilter = 'normal'
		self.Game.failState_setup = (0,1,2,3)

		self.eventActive = False
		for ID in self.afterIDs:
			try:				self.can.after_cancel(ID)
			except ValueError:	pass
		self.eventStartTime = 0

		for index, seg1 in enumerate(self.Game.snake[1:]):
			fail = False
			seg2 = self.Game.snake[index]
			test = (seg1[0]-seg2[0], seg1[1]-seg2[1])
			if abs(test[0]) > 1 or abs(test[1]) > 1:
				fail = True
				break

		if fail:
			self.Game.GAMEOVER_procedure()
			return None

		self.can.itemconfig('frame', outline='light blue')
		self.can.coords('Gauge2', self.Game.Gauge2Base[0], self.Game.emptyGaugePx_Y, self.Game.Gauge2Base[1], self.Game.emptyGaugePx_Y)



class PowerUp_ram(PowerUps_class):	
	# donne tête de flêche au serpent 
	# Permet de détruire les peaux mortes.
	def __init__(self, coord):

		self.coord_ = coord
		#self.POW = 0 # Placeholder pour self.PowerUp_instances[coord]['func']
		
		self.score_bonus = 1000
		self.score_mod = 2
		self.eventActive = False
		self.eventDurée = 6000
		self.event_timer = self.eventDurée
		self.afterIDs = []
		self.arrowID = 0

		self.blinker_deleteTimer = 5000 #ms
		self.blinker_on = False
		self.blinker_PanicTime = 2000 # ms avant la supression du PowerUp
		self.blinker_speed = 400
		self.blinker_counter = int(self.blinker_PanicTime / self.blinker_speed)

		self.rim_coul = 'cyan'
		self.trig_coul = 'grey'

		#Arrow shape utils
		self.cL, self.cH = self.grid.CellLARG/2, self.grid.CellHAUT/2

		# Preloads_
		self.after = self.can.after


	def activate(self):
		print('WrapAround ACTIF !')
		self.eventActive = True

		self.eventStartTime = time()

		self.Game.combo_timer = self.Game.combo_delay
		self.Game.Score_addBonus(self.score_bonus)

		self.can.coords('Gauge1', self.Game.Gauge1Base[0], self.Game.emptyGaugePx_Y, self.Game.Gauge1Base[1], self.Game.emptyGaugePx_Y-self.Game.fullGaugeLen)
		self._GaugeManager(self.PowerUp_instances[self.coord_]['func'])

		self.PowerUp_wipe(self.coord_)
		self.afterIDs += [self.after(self.eventDurée, self.stop)]
		#self.after_cancel(self.afterIDs[-1])
		print('STOP EVENTID :', self.afterIDs[-1])
		
		self.can.itemconfig('frame', outline='grey')

		self.Game.speedCap_actu = 'ram'
		self.Game.gearShift()
		
		self.Game.failState_setup = (0,1,2)

		self.can.itemconfig('Snake', fill='orange')
		#coup, tête = self.grid.find_coord(self.Game.snake[-2]), self.grid.find_coord(self.Game.tête)
		#self.can.create_line(	coup[0] + self.cL, coup[1] + self.cH, tête[0] + self.cL, tête[1] + self.cH,
		#						fill='orange' , arrow='last', arrowshape=[8, 10, 10], tags='arrow')

		self.anime()


	def stop(self):
		print('TIME TO STOP !!')

		self.eventActive = False
		for ID in self.afterIDs:
			try:				self.can.after_cancel(ID)
			except ValueError:	pass
		self.eventStartTime = 0

		self.Game.failState_setup = (0,1,2,3)

		self.Game.speedCap_actu = 'normal'
		self.Game.gearShift()

		self.can.itemconfig('frame', outline='light blue')
		self.can.coords('Gauge1', self.Game.Gauge1Base[0], self.Game.emptyGaugePx_Y, self.Game.Gauge1Base[1], self.Game.emptyGaugePx_Y)

		self.can.itemconfig('Snake', fill='light green')


	def anime(self):
		tupTête = tuple(self.Game.tête)
		if tupTête in self.Game.snake_peauMorte:
			scora = self.Game.score_actuelle
			self.can.delete(self.Game.snake_peauMorte.pop(tupTête))
			self.Game.Score_addBonus(self.score_bonus)
			print(f'La Peau Morte en {tupTête} a été détruite !')
		
		'''
		coup, tête = self.grid.find_coord(self.Game.snake[-2]), self.grid.find_coord(self.Game.tête)
		vect = (tête[0] - coup[0], tête[1] - coup[1])
		mag = self.hypot(*vect)
		sCoords = self.scaledCoords(mag, vect, mag*2)# = ((vect[0]/hypot)*r + x, (vect[1]/hypot)*r + y)
		sCoords = (sCoords[0] + coup[0], sCoords[1] + coup[1])
		self.can.coords('arrow', coup[0]+self.cL, coup[1]+self.cH, *sCoords)
		'''

		if self.eventActive and not self.Game.GAMEOVER:
			self.afterIDs += [self.after(self.Game.vitesse_actuelle,  self.anime)]
			self.afterIDs.pop(0)

